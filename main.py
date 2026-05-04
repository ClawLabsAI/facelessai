"""
FacelessAI Backend — Video Generation Server v2.0
FastAPI + FFmpeg + Pexels
Generates real MP4 videos from script + audio + stock clips
BREAKING CHANGE: audio_url REMOVED. Only audio_b64 accepted.
"""


import os
import re
import uuid
import httpx
import asyncio
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="FacelessAI Video Generator", version="1.0")

# Allow requests from GitHub Pages and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temp directory for generated files
TEMP_DIR = Path(tempfile.gettempdir()) / "facelessai"
TEMP_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────

class VideoRequest(BaseModel):
    audio_b64: str                      # Base64 encoded audio from browser
    audio_url: str = ""                 # Legacy field — kept for compatibility, ignored
    pexels_clips: list[str] = []        # List of Pexels video URLs
    script: str = ""
    title: str = "FacelessAI Video"
    lang: str = "es"
    subtitle_style: str = "viral"


class StatusResponse(BaseModel):
    job_id: str
    status: str   # pending, processing, done, error
    progress: int
    message: str
    download_url: Optional[str] = None


# Job tracking
jobs: dict = {}

# ─────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "FacelessAI Video Generator",
        "version": "1.0",
        "status": "running",
        "ffmpeg": check_ffmpeg()
    }

@app.get("/health")
async def health():
    return {"status": "ok", "ffmpeg": check_ffmpeg()}

def check_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return "available" if result.returncode == 0 else "not found"
    except FileNotFoundError:
        return "not installed"


# ─────────────────────────────────────────
# VIDEO GENERATION ENDPOINT
# ─────────────────────────────────────────

@app.post("/debug")
async def debug_request(req: VideoRequest):
    """Debug endpoint — echoes what it received"""
    return {
        "received": {
            "has_audio_b64": bool(req.audio_b64),
            "audio_b64_len": len(req.audio_b64) if req.audio_b64 else 0,
            "pexels_clips_count": len(req.pexels_clips),
            "pexels_clips_preview": req.pexels_clips[:2] if req.pexels_clips else [],
            "script_len": len(req.script),
            "title": req.title,
            "lang": req.lang,
        }
    }



@app.post("/generate", response_model=StatusResponse)
async def generate_video(req: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {"status": "pending", "progress": 0, "message": "Iniciando...", "download_url": None}
    background_tasks.add_task(process_video, job_id, req)
    return StatusResponse(job_id=job_id, status="pending", progress=0, message="Job creado — procesando...")


@app.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    j = jobs[job_id]
    return StatusResponse(
        job_id=job_id,
        status=j["status"],
        progress=j["progress"],
        message=j["message"],
        download_url=j.get("download_url")
    )


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "done":
        raise HTTPException(status_code=404, detail="Vídeo no disponible aún")
    filepath = TEMP_DIR / f"{job_id}_output.mp4"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(
        path=str(filepath),
        media_type="video/mp4",
        filename=f"facelessai_{job_id}.mp4"
    )


# ─────────────────────────────────────────
# CORE VIDEO PROCESSING
# ─────────────────────────────────────────

async def process_video(job_id: str, req: VideoRequest):
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    def update(status, progress, message):
        jobs[job_id] = {"status": status, "progress": progress, "message": message, "download_url": jobs[job_id].get("download_url")}

    try:
        # ── STEP 1: Save audio from base64 ──
        update("processing", 10, "Procesando audio...")
        audio_path = job_dir / "audio.mp3"
        import base64
        audio_data = base64.b64decode(req.audio_b64)
        audio_path.write_bytes(audio_data)

        # Get audio duration
        duration = get_audio_duration(str(audio_path))
        update("processing", 20, f"Audio: {duration:.1f}s descargado")

        # ── STEP 2: Download video clips ──
        update("processing", 30, f"Descargando {len(req.pexels_clips)} clips...")
        clip_paths = []

        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            for i, clip_url in enumerate(req.pexels_clips[:6]):  # max 6 clips
                try:
                    r = await client.get(clip_url)
                    clip_path = job_dir / f"clip_{i}.mp4"
                    clip_path.write_bytes(r.content)
                    clip_paths.append(str(clip_path))
                    update("processing", 30 + i * 5, f"Clip {i+1}/{len(req.pexels_clips)} descargado")
                except Exception as e:
                    print(f"Error downloading clip {i}: {e}")

        if not clip_paths:
            raise ValueError("No se pudieron descargar clips de Pexels")

        update("processing", 55, f"{len(clip_paths)} clips listos — preparando montaje...")

        # ── STEP 3: Process clips — crop to 9:16, normalize ──
        processed_clips = []
        clip_duration = duration / len(clip_paths)

        for i, clip_path in enumerate(clip_paths):
            out_path = job_dir / f"proc_{i}.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-i", clip_path,
                "-t", str(clip_duration),
                "-vf", (
                    # Crop to 9:16 ratio (vertical), scale to 1080x1920
                    "crop=in_h*9/16:in_h,"
                    "scale=1080:1920:force_original_aspect_ratio=increase,"
                    "crop=1080:1920,"
                    # Zoom effect: subtle ken burns
                    f"zoompan=z='min(zoom+0.0015,1.5)':d={int(clip_duration*30)}:s=1080x1920"
                ),
                "-r", "30",
                "-an",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                str(out_path)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            processed_clips.append(str(out_path))

        update("processing", 65, "Clips procesados — concatenando...")

        # ── STEP 4: Concatenate clips ──
        concat_list = job_dir / "concat.txt"
        concat_list.write_text("\n".join([f"file '{p}'" for p in processed_clips]))

        concat_path = job_dir / "concat.mp4"
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(concat_path)
        ], capture_output=True, check=True)

        update("processing", 72, "Clips concatenados — generando subtítulos...")

        # ── STEP 5: Generate SRT subtitles from script ──
        srt_path = job_dir / "subs.srt"
        generate_srt(req.script, duration, str(srt_path))

        update("processing", 78, "Subtítulos generados — montaje final...")

        # ── STEP 6: Final composition — concat + audio + subtitles ──
        output_path = TEMP_DIR / f"{job_id}_output.mp4"

        # Subtitle style
        subtitle_filter = get_subtitle_filter(str(srt_path), req.subtitle_style)

        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(concat_path),
            "-i", str(audio_path),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-t", str(duration),
            "-vf", subtitle_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "21",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-movflags", "+faststart",
            str(output_path)
        ], capture_output=True, check=True)

        # ── DONE ──
        file_size_mb = output_path.stat().st_size / 1024 / 1024
        jobs[job_id]["status"] = "done"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = f"✅ Vídeo listo — {duration:.1f}s · {file_size_mb:.1f}MB"
        jobs[job_id]["download_url"] = f"/download/{job_id}"

        # Cleanup temp files (keep output)
        import shutil
        shutil.rmtree(str(job_dir), ignore_errors=True)

    except subprocess.CalledProcessError as e:
        err = e.stderr.decode() if e.stderr else str(e)
        jobs[job_id] = {"status": "error", "progress": 0, "message": f"FFmpeg error: {err[-200:]}", "download_url": None}
    except Exception as e:
        jobs[job_id] = {"status": "error", "progress": 0, "message": f"Error: {str(e)}", "download_url": None}


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def get_audio_duration(path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True, text=True
    )
    import json
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def generate_srt(script: str, duration: float, output_path: str):
    """Split script into subtitle chunks and generate SRT file"""
    # Clean script — remove tags and annotations
    clean = re.sub(r'\[.*?\]', '', script)
    clean = re.sub(r'#\w+', '', clean)
    clean = re.sub(r'//.*', '', clean)
    clean = ' '.join(clean.split())

    # Split into chunks of ~5 words
    words = clean.split()
    chunk_size = 5
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    if not chunks:
        chunks = ["FacelessAI"]

    time_per_chunk = duration / len(chunks)
    srt_content = ""

    for i, chunk in enumerate(chunks):
        start = i * time_per_chunk
        end = (i + 1) * time_per_chunk
        srt_content += f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{chunk.upper()}\n\n"

    Path(output_path).write_text(srt_content, encoding='utf-8')


def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def get_subtitle_filter(srt_path: str, style: str) -> str:
    """Return FFmpeg subtitle filter string based on style"""
    # Escape path for FFmpeg
    safe_path = srt_path.replace('\\', '/').replace(':', '\\:')

    if style == "viral":
        return (
            f"subtitles='{safe_path}':force_style='"
            "FontName=Impact,FontSize=22,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,Outline=3,Shadow=2,"
            "Alignment=2,MarginV=60,"
            "Bold=1'"
        )
    elif style == "minimal":
        return (
            f"subtitles='{safe_path}':force_style='"
            "FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,Outline=2,"
            "Alignment=2,MarginV=40'"
        )
    else:  # classic
        return (
            f"subtitles='{safe_path}':force_style='"
            "FontName=Arial,FontSize=18,PrimaryColour=&H00FFFF00,"
            "OutlineColour=&H00000000,Outline=2,"
            "Alignment=2,MarginV=50'"
        )


# ─────────────────────────────────────────
# YOUTUBE ANALYTICS PROXY
# ─────────────────────────────────────────

@app.get("/yt/channel-stats")
async def yt_channel_stats(channel_id: str, access_token: str):
    """Proxy YouTube Data API v3 channel stats (avoids CORS in browser)"""
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "statistics,snippet", "id": channel_id},
            headers={"Authorization": f"Bearer {access_token}"}
        )
    if r.status_code == 401:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")
    if not r.is_success:
        raise HTTPException(status_code=r.status_code, detail="YouTube API error")
    data = r.json()
    items = data.get("items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    item = items[0]
    stats = item.get("statistics", {})
    snippet = item.get("snippet", {})
    return {
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0))
    }


# ─────────────────────────────────────────
# CLIPPING ENDPOINTS
# ─────────────────────────────────────────

class ClipRequest(BaseModel):
    youtube_url: str
    openai_api_key: str
    moments: list[dict] = []   # [{start, end, title}] — if empty, auto-detect
    subtitle_style: str = "viral"
    format: str = "9:16"       # 9:16 vertical or 16:9 horizontal

class TranscribeRequest(BaseModel):
    youtube_url: str
    openai_api_key: str
    lang: str = "es"

# Transcription jobs store
transcribe_jobs: dict = {}
clip_jobs: dict = {}

@app.post("/transcribe")
async def transcribe_video(req: TranscribeRequest, background_tasks: BackgroundTasks):
    """Download YouTube video and transcribe with Whisper"""
    job_id = str(uuid.uuid4())[:8]
    transcribe_jobs[job_id] = {"status": "pending", "progress": 0, "message": "Iniciando...", "transcript": None, "duration": 0}
    background_tasks.add_task(do_transcribe, job_id, req)
    return {"job_id": job_id, "status": "pending"}

@app.get("/transcribe/status/{job_id}")
async def transcribe_status(job_id: str):
    if job_id not in transcribe_jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return transcribe_jobs[job_id]

@app.post("/clip")
async def create_clip(req: ClipRequest, background_tasks: BackgroundTasks):
    """Create vertical clips from YouTube video"""
    job_id = str(uuid.uuid4())[:8]
    clip_jobs[job_id] = {"status": "pending", "progress": 0, "message": "Iniciando...", "clips": []}
    background_tasks.add_task(do_clip, job_id, req)
    return {"job_id": job_id, "status": "pending"}

@app.get("/clip/status/{job_id}")
async def clip_status(job_id: str):
    if job_id not in clip_jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return clip_jobs[job_id]

@app.get("/clip/download/{job_id}/{clip_index}")
async def download_clip(job_id: str, clip_index: int):
    filepath = TEMP_DIR / f"{job_id}_clip_{clip_index}.mp4"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Clip no encontrado")
    return FileResponse(str(filepath), media_type="video/mp4", filename=f"clip_{job_id}_{clip_index}.mp4")

async def do_transcribe(job_id: str, req: TranscribeRequest):
    job_dir = TEMP_DIR / f"tr_{job_id}"
    job_dir.mkdir(exist_ok=True)

    def update(status, progress, message, **kwargs):
        transcribe_jobs[job_id] = {"status": status, "progress": progress, "message": message, **kwargs}

    try:
        update("processing", 10, "Descargando audio de YouTube...")
        audio_path = str(job_dir / "audio.mp3")

        # Download audio only with yt-dlp
        result = subprocess.run([
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--output", audio_path.replace(".mp3", ".%(ext)s"),
            "--no-playlist",
            "--max-filesize", "200m",
            req.youtube_url
        ], capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise ValueError(f"yt-dlp error: {result.stderr[-300:]}")

        # Find the downloaded file
        import glob
        files = glob.glob(str(job_dir / "audio.*"))
        if not files:
            raise ValueError("No se pudo descargar el audio")
        audio_file = files[0]

        update("processing", 40, "Obteniendo duración del vídeo...")
        duration = get_audio_duration(audio_file)
        update("processing", 45, f"Duración: {int(duration//60)}min {int(duration%60)}s · Transcribiendo con Whisper...")

        # Transcribe with OpenAI Whisper
        from openai import OpenAI
        client = OpenAI(api_key=req.openai_api_key)

        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=req.lang if req.lang != "lat" else "es",
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )

        # Format segments
        segments = []
        for seg in (transcript.segments or []):
            segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip()
            })

        update("done", 100, f"✅ Transcripción completa · {len(segments)} segmentos · {int(duration//60)}min",
               transcript=segments, duration=round(duration), full_text=transcript.text)

        import shutil
        shutil.rmtree(str(job_dir), ignore_errors=True)

    except Exception as e:
        update("error", 0, f"Error: {str(e)}")


async def do_clip(job_id: str, req: ClipRequest):
    job_dir = TEMP_DIR / f"cl_{job_id}"
    job_dir.mkdir(exist_ok=True)

    def update(status, progress, message, **kwargs):
        clip_jobs[job_id] = {"status": status, "progress": progress, "message": message, "clips": clip_jobs[job_id].get("clips", []), **kwargs}

    try:
        update("processing", 5, "Descargando vídeo de YouTube...")

        video_path = str(job_dir / "video.mp4")
        result = subprocess.run([
            "yt-dlp",
            "--format", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
            "--output", video_path,
            "--no-playlist",
            "--max-filesize", "500m",
            "--merge-output-format", "mp4",
            req.youtube_url
        ], capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise ValueError(f"yt-dlp error: {result.stderr[-300:]}")

        # Find downloaded video
        import glob
        files = glob.glob(str(job_dir / "video.*"))
        if not files:
            raise ValueError("No se pudo descargar el vídeo")
        video_file = files[0]

        update("processing", 30, f"Vídeo descargado · Procesando {len(req.moments)} momentos...")

        clips_created = []
        for i, moment in enumerate(req.moments):
            start = moment.get("start", 0)
            end = moment.get("end", start + 60)
            title = moment.get("title", f"Clip {i+1}")
            duration_clip = end - start

            update("processing", 30 + int(i * 60 / max(len(req.moments), 1)),
                   f"Procesando clip {i+1}/{len(req.moments)}: {title[:40]}...")

            out_path = TEMP_DIR / f"{job_id}_clip_{i}.mp4"

            # Cut + convert to 9:16 vertical
            if req.format == "9:16":
                vf = (
                    "crop=ih*9/16:ih,"
                    "scale=1080:1920:force_original_aspect_ratio=increase,"
                    "crop=1080:1920"
                )
            else:
                vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"

            # Generate SRT for this clip
            srt_path = job_dir / f"subs_{i}.srt"
            # Simple subtitle: just show the title/topic
            srt_content = f"1\n00:00:00,000 --> 00:00:{min(int(duration_clip), 59):02d},000\n{title.upper()}\n\n"
            srt_path.write_text(srt_content)

            safe_srt = str(srt_path).replace('\\', '/').replace(':', '\\:')
            subtitle_filter = get_subtitle_filter(str(srt_path), req.subtitle_style)

            cmd = [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-i", video_file,
                "-t", str(duration_clip),
                "-vf", f"{vf},{subtitle_filter.split(',', 1)[-1] if ',' in subtitle_filter else subtitle_filter}",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "22",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                str(out_path)
            ]

            subprocess.run(cmd, capture_output=True, timeout=300)

            if out_path.exists():
                size_mb = round(out_path.stat().st_size / 1024 / 1024, 1)
                clips_created.append({
                    "index": i,
                    "title": title,
                    "start": start,
                    "end": end,
                    "duration": duration_clip,
                    "size_mb": size_mb,
                    "download_url": f"/clip/download/{job_id}/{i}"
                })

        clip_jobs[job_id]["clips"] = clips_created
        update("done", 100, f"✅ {len(clips_created)} clips generados · Listos para descargar", clips=clips_created)

        import shutil
        shutil.rmtree(str(job_dir), ignore_errors=True)

    except Exception as e:
        update("error", 0, f"Error: {str(e)}")
