from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="Mini Spotify Clone API - iTunes Version")

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def featured():
    """
    Return featured playlists (hardcoded queries)
    """
    featured_queries = ["Ed Sheeran", "The Weeknd", "Taylor Swift", "Drake"]
    featured_songs = []

    async with httpx.AsyncClient() as client:
        for query in featured_queries:
            url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=3"
            response = await client.get(url)
            data = response.json()
            for item in data.get("results", []):
                featured_songs.append({
                    "title": item.get("trackName"),
                    "artist": item.get("artistName"),
                    "album": item.get("collectionName"),
                    "audio_url": item.get("previewUrl"),
                    "image": item.get("artworkUrl100").replace("100x100", "500x500"),
                    "id": item.get("trackId")
                })

    return {"playlists": [{"name": "Featured", "songs": featured_songs}]}
