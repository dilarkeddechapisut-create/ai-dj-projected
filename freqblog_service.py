import requests
import streamlit as st

FREQBLOG_API_URL = "https://api.freqblog.com"

@st.cache_data(ttl=86400)
def get_audio_features(title: str, artist: str, spotify_id: str = None) -> dict:
    """
    ดึงข้อมูล Audio Features จาก FreqBlog API
    รองรับทั้งการค้นหาด้วยชื่อเพลง + ศิลปิน (/lookup) และ Spotify ID (/v1/audio-features/{spotify_id})
    """
    api_key = st.secrets.get("FREQBLOG_API_KEY", "")
    headers = {}
    if api_key:
        headers["X-Api-Key"] = api_key

    # 1. ค้นหาด้วยชื่อเพลง และชื่อศิลปิน ผ่าน Endpoint /lookup
    try:
        params = {"track": title, "artist": artist}
        res = requests.get(f"{FREQBLOG_API_URL}/lookup", params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict) and "energy" in data:
                return {
                    "energy": float(data.get("energy", 0.5)),
                    "valence": float(data.get("valence", 0.5)),
                    "danceability": float(data.get("danceability", 0.5)),
                    "acousticness": float(data.get("acousticness", 0.5)),
                    "bpm": float(data.get("bpm", 120)),
                    "mood": data.get("mood", "neutral")
                }
    except Exception as e:
        print(f"FreqBlog Lookup Error: {e}")

    # 2. กรณีค้นด้วยชื่อไม่พบ แต่มี spotify_id ให้ลองเรียก /v1/audio-features/{id}
    if spotify_id:
        try:
            res = requests.get(f"{FREQBLOG_API_URL}/v1/audio-features/{spotify_id}", headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, dict) and "energy" in data:
                    return {
                        "energy": float(data.get("energy", 0.5)),
                        "valence": float(data.get("valence", 0.5)),
                        "danceability": float(data.get("danceability", 0.5)),
                        "acousticness": float(data.get("acousticness", 0.5)),
                        "bpm": float(data.get("tempo", data.get("bpm", 120))),
                        "mood": data.get("mood", "neutral")
                    }
        except Exception as e:
            print(f"FreqBlog ID Error: {e}")

    # ค่าเริ่มต้นสำรอง (Fallback) กรณีหาไม่เจอหรือเกิด Error
    return {
        "energy": 0.5,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": 0.5,
        "bpm": 120.0,
        "mood": "neutral"
    }