import requests
import re

def get_track_preview(track_name, artist_name):
    """
    ค้นหาข้อมูลเพลงและดึงลิงก์พรีวิว 30 วินาที จาก iTunes หรือ Deezer
    คืนค่า (รูปปก, ลิงก์พรีวิวเสียง, ลิงก์ฟังเพลงเต็ม)
    """
    clean_title = re.sub(r'[\(\[\-\~].*?[\)\]\-\~]', '', str(track_name)).strip()
    clean_artist = str(artist_name).split(',')[0].strip()
    
    # 1. ลองค้นหาจาก iTunes API ก่อน
    try:
        query = f"{clean_title} {clean_artist}"
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&limit=1&entity=song"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            data = res.json()
            if data.get('resultCount', 0) > 0:
                t = data['results'][0]
                img = t.get('artworkUrl100', '').replace('100x100bb', '500x500bb')
                prev = t.get('previewUrl', None)
                link = t.get('trackViewUrl', None)
                if prev: return img, prev, link
    except Exception:
        pass

    # 2. ลองค้นหาจาก Deezer API (สำรอง)
    try:
        query_d = f"{clean_title} {clean_artist}"
        url_d = f"https://api.deezer.com/search?q={requests.utils.quote(query_d)}&limit=1"
        res_d = requests.get(url_d, timeout=4)
        if res_d.status_code == 200:
            data_d = res_d.json()
            if data_d.get('data') and len(data_d['data']) > 0:
                t = data_d['data'][0]
                img = t.get('album', {}).get('cover_xl') or t.get('album', {}).get('cover_big')
                prev = t.get('preview', None)
                link = t.get('link', None)
                if prev: return img, prev, link
    except Exception:
        pass

    return None, None, None