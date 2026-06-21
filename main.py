from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(
    title="Video Stream Extractor API",
    description="A simple API to extract direct video stream URLs using yt-dlp"
)

# Enable CORS so you can call this API from web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API is running. Use /extract?url=YOUR_URL to get the video stream."}

@app.get("/extract")
def extract_video_info(url: str = Query(..., description="The video URL to extract metadata from")):
    ydl_opts = {
        'format': 'best',  # Fetches the best pre-merged video/audio format available
        'noplaylist': True,
        'quiet': True,
        # Avoid getting geo-blocked if running on cloud servers
        'nocheckcertificate': True, 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # download=False ensures we only fetch metadata, making it instant
            info = ydl.extract_info(url, download=False)
            
            # Extract title and direct stream URL
            video_title = info.get('title')
            video_url = info.get('url') or (info.get('formats', [{}])[-1].get('url') if info.get('formats') else None)
            
            if not video_url:
                raise HTTPException(
                    status_code=400, 
                    detail="Direct downloadable stream URL could not be found for this video."
                )
                
            return {
                "status": "success",
                "title": video_title,
                "download_url": video_url,
                "duration": info.get('duration'),
                "thumbnail": info.get('thumbnail')
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"yt-dlp extraction error: {str(e)}")
