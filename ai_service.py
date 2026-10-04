import requests
import urllib.parse

def get_album_cover(song_title: str, artist: str = "") -> str:
    """ดึง URL รูปปกเพลงจริงจาก iTunes API อัตโนมัติ"""
    try:
        query = f"{song_title} {artist}".strip()
        encoded_query = urllib.parse.quote(query)
        url = f"https://itunes.apple.com/search?term={encoded_query}&entity=song&limit=1"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("resultCount", 0) > 0:
                artwork_url = data["results"][0].get("artworkUrl100", "")
                # ขยายขนาดรูปปกเป็น 600x600 px
                return artwork_url.replace("100x100bb", "600x600bb")
    except Exception as e:
        print(f"Error fetching cover image: {e}")
    
    # รูปสำรองกรณีหาไม่พบ
    return "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop"

def get_playlist_from_ai(prompt: str):
    """
    ฟังก์ชันส่งคืนรายการเพลงพร้อมรูปปก
    """
    try:
        # TODO: ส่วนนี้เชื่อมต่อกับ AI API (เช่น OpenAI/Gemini) ตามที่คุณต้องการ
        # ตัวอย่างเพลงที่ดึงมาใช้งาน:
        raw_songs = [
            {"title": "Weightless", "artist": "Marconi Union"},
            {"title": "Cornfield Chase", "artist": "Hans Zimmer"},
            {"title": "ถ้าเธอต้องเลือก", "artist": "ILLSLICK"}
        ]
        
        playlist = []
        for song in raw_songs:
            # ดึงรูปปกเพลงของแต่ละเพลง
            cover_url = get_album_cover(song["title"], song.get("artist", ""))
            playlist.append({
                "title": song["title"],
                "artist": song["artist"],
                "cover_url": cover_url
            })
        
        return playlist

    except Exception as e:
        print(f"Error in ai_service: {e}")
        return []
