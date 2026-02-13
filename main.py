from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import httpx
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Mini Spotify Clone API - iTunes Version")

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/featured", StaticFiles(directory="featured", html=False), name="static")

@app.get("/")
def home():
    return {"message": "Mini Spotify Clone API running"}

@app.get("/search")
async def search(query: str):
    """
    Search for songs on iTunes and return top 10 results with playable preview URLs
    """
    url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=10"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("trackName"),
            "artist": item.get("artistName"),
            "album": item.get("collectionName"),
            "audio_url": item.get("previewUrl"),  # 🔥 Playable in React Native
            "image": item.get("artworkUrl100").replace("100x100", "500x500"),
            "id": item.get("trackId")
        })

    return {"results": results}

@app.get("/featured")
def featured():
    try:
        with open("featured.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        return {"error": str(e)}
