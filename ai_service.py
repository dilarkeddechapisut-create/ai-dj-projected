import google.generativeai as genai
import json
import streamlit as st

def get_playlist_from_ai(mood_text, num_songs):
    """วิเคราะห์ความรู้สึกและสร้าง Playlist คืนค่าเป็น JSON"""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("กรุณาตั้งค่า GEMINI_API_KEY ใน Secrets")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.5-flash')

    prompt = f"""
    ผู้ใช้มีความรู้สึกดังนี้: "{mood_text}"
    กรุณาทำหน้าที่เป็น AI DJ ผู้เห็นอกเห็นใจ
    1. ให้คำพูดให้กำลังใจ/เข้าอกเข้าใจผู้ใช้ภาพรวมสั้นๆ 1 ย่อหน้า
    2. แนะนำเพลงจำนวน {num_songs} เพลง ที่เข้ากับอารมณ์นี้ (เน้นเพลงดังที่มีใน Spotify)
    
    ส่งคำตอบกลับมาในรูปแบบ JSON เท่านั้น โครงสร้างดังนี้:
    {{
        "encouragement": "คำพูดให้กำลังใจ...",
        "songs": [
            {{"title": "ชื่อเพลง", "artist": "ชื่อศิลปิน", "reason": "เหตุผลที่เลือกเพลงนี้ให้ (1 ประโยค)"}}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        json_str = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(json_str)
        return data
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์ AI: {e}")
        return None
