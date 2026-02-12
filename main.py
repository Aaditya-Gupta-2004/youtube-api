from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from yt_dlp import YoutubeDL
import os
import json
import threading
import time
from datetime import datetime, timedelta

app = FastAPI(title="Mini Spotify Clone API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_songs"
os.makedirs(TEMP_DIR, exist_ok=True)

# -----------------------------
# YT-DLP Base Options
# -----------------------------
def get_ydl_opts(video_id):
    return {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "outtmpl": os.path.join(TEMP_DIR, f"{video_id}.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

# -----------------------------
# Convert Function
# -----------------------------
def convert_to_mp3(video_id):
    file_path = os.path.join(TEMP_DIR, f"{video_id}.mp3")

    if os.path.exists(file_path):
        return file_path  # already converted

    url = f"https://www.youtube.com/watch?v={video_id}"

    with YoutubeDL(get_ydl_opts(video_id)) as ydl:
        ydl.download([url])

    return file_path

# -----------------------------
# Cleanup Thread
# -----------------------------
def cleanup_old_files():
    while True:
        now = datetime.now()
        for file in os.listdir(TEMP_DIR):
            path = os.path.join(TEMP_DIR, file)
            if os.path.isfile(path):
                created = datetime.fromtimestamp(os.path.getctime(path))
                if now - created > timedelta(hours=1):
                    try:
                        os.remove(path)
                        print(f"Deleted: {file}")
                    except:
                        pass
        time.sleep(600)  # check every 10 minutes

threading.Thread(target=cleanup_old_files, daemon=True).start()

# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def home():
    return {"message": "Mini Spotify Clone API running"}

@app.get("/search")
def search(query: str):
    search_opts = {
        "quiet": True,
        "default_search": "ytsearch5",
        "noplaylist": True,
    }

    with YoutubeDL(search_opts) as ydl:
        info = ydl.extract_info(query, download=False)

        results = []
        for entry in info.get("entries", []):
            results.append({
                "title": entry.get("title"),
                "video_id": entry.get("id"),
                "thumbnail": entry.get("thumbnail"),
            })

    return {"results": results}


@app.get("/play/{video_id}")
def play(video_id: str):
    """
    Convert on-demand if not exists
    """
    try:
        file_path = convert_to_mp3(video_id)
        return FileResponse(file_path, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/featured")
def featured():
    """
    Load featured.json and pre-convert songs
    """
    try:
        with open("featured.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Pre-download featured songs
        for song in data.get("songs", []):
            video_id = song.get("video_id")
            if video_id:
                try:
                    convert_to_mp3(video_id)
                except:
                    pass

        return data

    except Exception as e:
        return {"error": str(e)}
