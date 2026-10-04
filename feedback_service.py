import requests
import streamlit as st

def save_mood_history(user_email, mood_text, persona="", energy_level=""):
    """ บันทึกประวัติการบอกอารมณ์ของผู้ใช้แต่ละคนลง Google Sheets """
    apps_script_url = st.secrets.get("APPS_SCRIPT_URL", "")

    if not apps_script_url:
        print("⚠️ Warning: APPS_SCRIPT_URL is not set in Secrets.")
        return False

    try:
        payload = {
            "action_type": "MOOD_LOG",
            "user_email": user_email,
            "mood_text": mood_text,
            "persona": persona,
            "energy_level": energy_level,
            "song_name": "-",
            "artist": "-",
            "feedback": "Search"
        }
        
        response = requests.post(
            apps_script_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.text.strip() == "Success"
        
    except Exception as e:
        print(f"API Error (save_mood_history): {e}")
        return False


def save_feedback(user_email, mood_text, song_name="", artist="", is_liked=True):
    """ บันทึกประวัติการกดถูกใจ/ยกเลิกถูกใจเพลงของผู้ใช้ลง Google Sheets """
    apps_script_url = st.secrets.get("APPS_SCRIPT_URL", "")

    if not apps_script_url:
        print("⚠️ Warning: APPS_SCRIPT_URL is not set in Secrets.")
        return False

    try:
        feedback_status = "Like" if is_liked else "Dislike"
        payload = {
            "action_type": "LIKE_LOG",
            "user_email": user_email,
            "mood_text": mood_text,
            "persona": "-",
            "energy_level": "-",
            "song_name": song_name,
            "artist": artist,
            "feedback": feedback_status
        }
        
        response = requests.post(
            apps_script_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.text.strip() == "Success"
        
    except Exception as e:
        print(f"API Error (save_feedback): {e}")
        return False

save_favorite_song = save_feedback
