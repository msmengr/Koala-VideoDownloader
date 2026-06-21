from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

app = FastAPI(title="Video Stream Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API is running."}

@app.get("/extract")
def extract_video_info(url: str = Query(..., description="The video URL to extract metadata from")):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'nocheckcertificate': True,
        
        # 1. Enable TLS & Browser Impersonation (Tricks TikTok's bot mitigation systems)
        'impersonate': ImpersonateTarget.from_str('chrome'),
        
        # 2. Inject realistic desktop HTTP request headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_title = info.get('title')
            video_url = info.get('url') or (info.get('formats', [{}])[-1].get('url') if info.get('formats') else None)
            
            if not video_url:
                raise HTTPException(status_code=400, detail="Direct stream URL not found.")
                
            return {
                "status": "success",
                "title": video_title,
                "download_url": video_url,
                "duration": info.get('duration'),
                "thumbnail": info.get('thumbnail')
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")
