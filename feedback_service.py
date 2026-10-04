import requests
import streamlit as st

def save_mood_history(user_email, mood_text, persona="", energy_level=""):
    """ บันทึกประวัติการบอกอารมณ์ของผู้ใช้ลง Google Sheets """
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
        
        response = requests.get(
            apps_script_url,
            params=payload,
            timeout=10
        )
        return "Success" in response.text
        
    except Exception as e:
        print(f"API Error (save_mood_history): {e}")
        return False


def save_feedback(user_email, mood_text, song_name="", artist="", is_liked=True):
    """ บันทึกประวัติการกดถูกใจ/ยกเลิกถูกใจเพลงลง Google Sheets """
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
        
        response = requests.get(
            apps_script_url,
            params=payload,
            timeout=10
        )
        return "Success" in response.text
        
    except Exception as e:
        print(f"API Error (save_feedback): {e}")
        return False

save_favorite_song = save_feedback


def get_user_saved_data(user_email):
    """ ดึงประวัติการใช้งานและเพลงโปรดของ User จาก Google Sheets """
    apps_script_url = st.secrets.get("APPS_SCRIPT_URL", "")

    if not apps_script_url or not user_email:
        return {"history": [], "favorites": []}

    try:
        response = requests.get(
            apps_script_url,
            params={"action": "FETCH_DATA", "user_email": user_email},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"API Error (get_user_saved_data): {e}")

    return {"history": [], "favorites": []}
