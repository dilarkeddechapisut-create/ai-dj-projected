import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

client_id = st.secrets["SPOTIFY_CLIENT_ID"]
client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

def search_spotify_track(song_title, artist_name):
    """ค้นหาเพลงและดึงข้อมูลพื้นฐาน"""
    query = f"track:{song_title} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)
    
    tracks = results.get('tracks', {}).get('items', [])
    if not tracks:
        return None
        
    track = tracks[0]
    track_id = track['id']
    
    # ดึงค่า Audio Features (ใส่ Try-Except ดัก Error จากนโยบายใหม่ของ Spotify)
    try:
        features = sp.audio_features(track_id)[0]
        energy = features['energy'] if features else 0.5
        valence = features['valence'] if features else 0.5
        danceability = features['danceability'] if features else 0.5
    except Exception as e:
        # หาก Spotify API บล็อก จะตั้งค่ากลางๆ ไว้ไม่ให้แอปพัง
        print(f"Spotify Audio Features API ถูกจำกัด: {e}")
        energy, valence, danceability = 0.5, 0.5, 0.5
    
    return {
        "id": track_id,
        "name": track['name'],
        "artist": track['artists'][0]['name'],
        "album_cover": track['album']['images'][0]['url'],
        "preview_url": track.get('preview_url'),
        "spotify_url": track['external_urls']['spotify'],
        "energy": energy,
        "valence": valence,
        "danceability": danceability
    }
