import requests
import streamlit as st

def save_feedback(mood_text, is_liked=True, song_name="", artist=""):
    """ส่งข้อมูลประวัติการกดถูกใจเพลงไปยัง Google Sheets อย่างปลอดภัย"""
    # ดึง URL จาก secrets แบบปลอดภัย (หากยังไม่ตั้งค่าจะไม่ทำให้แอปพัง)
    apps_script_url = st.secrets.get("APPS_SCRIPT_URL", "")

    if not apps_script_url:
        print("⚠️ Warning: APPS_SCRIPT_URL is not set in Secrets.")
        return False

    try:
        feedback_status = "Like" if is_liked else "Dislike"
        payload = {
            "mood_text": mood_text,
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
        print(f"API Error: {e}")
        return False

# ตั้ง Alias รองรับการเรียกทั้งสองชื่อเพื่อกัน Error
save_favorite_song = save_feedback
