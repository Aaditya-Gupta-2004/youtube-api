from fastapi import FastAPI
from yt_dlp import YoutubeDL
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mini Spotify Clone API")

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# yt-dlp options for audio only
YDL_OPTS = {
    "format": "bestaudio/best",  # get best audio stream
    "quiet": True,
    "noplaylist": True,
    "extract_flat": "in_playlist",  # no videos list extraction
    "js_runtime": "node",           # Node.js must be installed
}

@app.get("/")
def home():
    return {"message": "Mini Spotify Clone API running"}

@app.get("/search")
def search(query: str):
    """
    Search for songs and return top 5 results with video IDs and titles
    """
    search_opts = YDL_OPTS.copy()
    search_opts["default_search"] = "ytsearch5"  # top 5 results
    with YoutubeDL(search_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        results = []
        for entry in info.get("entries", []):
            results.append({
                "title": entry.get("title"),
                "video_id": entry.get("id"),
            })
    return {"results": results}

@app.get("/play/{video_id}")
def play(video_id: str):
    """
    Return direct audio URL for a YouTube video
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    with YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info.get("url")  # direct audio URL
        title = info.get("title")
    return {"audio_url": audio_url, "title": title}


@app.get("/search")
def search(query: str):
    """
    Search for songs and return top 5 results with video IDs, titles, and thumbnails
    """
    search_opts = YDL_OPTS.copy()
    search_opts["default_search"] = "ytsearch5"  # top 5 results
    with YoutubeDL(search_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        results = []
        for entry in info.get("entries", []):
            results.append({
                "title": entry.get("title"),
                "video_id": entry.get("id"),
                "thumbnail": entry.get("thumbnail"),  # <-- add this
            })
    return {"results": results}
