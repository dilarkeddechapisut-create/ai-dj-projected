import requests
import urllib.parse
import re

DEFAULT_COVER = "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80"
# ไฟล์เสียงตัวอย่างสำรองกรณีไม่พบ MP3 จากระบบ
FALLBACK_AUDIO_URL = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=music-112199.mp3"

def get_track_preview(track_name, artist_name):
    """
    ดึงรูปปกและไฟล์พรีวิวเสียง 30 วินาที จาก Deezer API (หลัก) และ iTunes API (สำรอง)
    พร้อมระบบ Fallback อัตโนมัติเพื่อให้กดฟังตัวอย่างเพลงได้เสมอ
    """
    clean_title = re.sub(r'[\(\[\-\~].*?[\)\]\-\~]', '', str(track_name)).strip()
    clean_artist = str(artist_name).split(',')[0].strip()
    query_str = f"{clean_title} {clean_artist}".strip()
    
    img_url, preview_url, full_url = None, None, None

    # 1. ค้นหาจาก Deezer API (เสถียรที่สุดสำหรับตัวอย่างไฟล์ MP3)
    try:
        deezer_url = f"https://api.deezer.com/search?q={urllib.parse.quote(query_str)}&limit=3"
        res = requests.get(deezer_url, timeout=5)
        if res.status_code == 200:
            data = res.json().get('data', [])
            if data:
                target = data[0]
                for item in data:
                    if clean_artist.lower() in item.get('artist', {}).get('name', '').lower():
                        target = item
                        break
                
                preview_url = target.get('preview')
                img_url = target.get('album', {}).get('cover_xl') or target.get('album', {}).get('cover_big')
                full_url = target.get('link')
    except Exception as e:
        print(f"Deezer Fetch Error: {e}")

    # 2. ค้นหาจาก iTunes API กรณี Deezer ไม่พบข้อมูล
    if not preview_url or not img_url:
        try:
            itunes_url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query_str)}&limit=3&entity=song"
            res = requests.get(itunes_url, timeout=5)
            if res.status_code == 200:
                results = res.json().get('results', [])
                if results:
                    target = results[0]
                    for item in results:
                        if clean_artist.lower() in item.get('artistName', '').lower():
                            target = item
                            break
                    if not preview_url:
                        preview_url = target.get('previewUrl')
                    if not img_url:
                        img_url = target.get('artworkUrl100', '').replace('100x100bb', '500x500bb')
                    if not full_url:
                        full_url = target.get('trackViewUrl')
        except Exception as e:
            print(f"iTunes Fetch Error: {e}")

    # 3. Fallback Safety Nets
    if not img_url:
        img_url = DEFAULT_COVER
        
    if not preview_url:
        preview_url = FALLBACK_AUDIO_URL

    if not full_url:
        full_url = f"https://open.spotify.com/search/{urllib.parse.quote(query_str)}"

    return img_url, preview_url, full_url
