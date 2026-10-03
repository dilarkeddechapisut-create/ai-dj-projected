import requests
import streamlit as st

# ดึง URL จาก Secrets แทนการพิมพ์ลงไปตรงๆ
APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]

def save_feedback(mood_text, is_liked):
    """ส่งข้อมูลไปยัง Google Apps Script Web App"""
    try:
        feedback_status = "Like" if is_liked else "Dislike"
        
        payload = {
            "mood_text": mood_text,
            "feedback": feedback_status
        }
        
        response = requests.post(APPS_SCRIPT_URL, data=payload)
        
        return response.text == "Success"
        
    except Exception as e:
        print(f"API Error: {e}")
        return False