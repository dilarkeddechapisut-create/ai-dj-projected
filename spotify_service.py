import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

def get_spotify_client():
    client_id = st.secrets.get("SPOTIFY_CLIENT_ID", "")
    client_secret = st.secrets.get("SPOTIFY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None
    try:
        return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        ))
    except Exception as e:
        print(f"Spotify Init Error: {e}")
        return None

sp = get_spotify_client()

def search_spotify_track(song_title, artist_name):
    """ค้นหาเพลงใน Spotify เพื่อเอา รูปปก ลิงก์ และ ID โดยปรับปรุงระบบค้นหาให้แม่นยำขึ้น"""
    if not sp:
        return None

    try:
        query = f"track:{song_title} artist:{artist_name}"
        results = sp.search(q=query, type='track', limit=1)
        tracks = results.get('tracks', {}).get('items', [])
        
        if not tracks:
            query_fallback = f"{song_title} {artist_name}"
            results = sp.search(q=query_fallback, type='track', limit=1)
            tracks = results.get('tracks', {}).get('items', [])

        if not tracks:
            return None
            
        track = tracks[0]
        track_id = track['id']
        album_cover = track['album']['images'][0]['url'] if track['album']['images'] else None
        
        return {
            "id": track_id,
            "name": track['name'],
            "artist": ", ".join([a['name'] for a in track['artists']]),
            "album_cover": album_cover,
            "preview_url": track.get('preview_url'),
            "spotify_url": track['external_urls']['spotify']
        }
    except Exception as e:
        print(f"Spotify Search Error: {e}")
        return None
