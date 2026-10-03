import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

# ดึง Key จาก st.secrets (ตั้งค่าใน Streamlit Cloud หรือไฟล์ .streamlit/secrets.toml)
client_id = st.secrets["SPOTIFY_CLIENT_ID"]
client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

def search_spotify_track(song_title, artist_name):
    """ค้นหาเพลงและดึงข้อมูลพื้นฐาน + Audio Features สำหรับทำกราฟ"""
    query = f"track:{song_title} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)
    
    tracks = results.get('tracks', {}).get('items', [])
    if not tracks:
        return None
        
    track = tracks[0]
    track_id = track['id']
    
    # ดึงค่า Audio Features (เพื่อนำไปทำกราฟ)
    features = sp.audio_features(track_id)[0]
    
    return {
        "id": track_id,
        "name": track['name'],
        "artist": track['artists'][0]['name'],
        "album_cover": track['album']['images'][0]['url'],
        "preview_url": track.get('preview_url'), # ลิงก์ 30 วิ (บางเพลงอาจไม่มี ขึ้นอยู่กับลิขสิทธิ์)
        "spotify_url": track['external_urls']['spotify'],
        "energy": features['energy'] if features else 0,
        "valence": features['valence'] if features else 0,
        "danceability": features['danceability'] if features else 0
    }