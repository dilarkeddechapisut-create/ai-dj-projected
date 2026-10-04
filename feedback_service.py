import requests
import streamlit as st

APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]

def save_favorite_song(mood_text, song_name, artist="", is_liked=True):
    """ส่งข้อมูลประวัติการกดถูกใจเพลงไปยัง Google Sheets"""
    try:
        feedback_status = "Like" if is_liked else "Dislike"
        
        payload = {
            "mood_text": mood_text,
            "song_name": song_name,
            "artist": artist,
            "feedback": feedback_status
        }
        
        # ส่งข้อมูลแบบ JSON
        response = requests.post(
            APPS_SCRIPT_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        return response.text.strip() == "Success"
        
    except Exception as e:
        print(f"API Error: {e}")
        return False
