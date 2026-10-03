import google.generativeai as genai
import streamlit as st
import json

# ดึงค่า API Key จากระบบ Secrets ของ Streamlit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ใช้โมเดล gemini-1.5-flash
model = genai.GenerativeModel('gemini-3.5-flash')

# ... (โค้ดส่วนอื่นใน ai_service.py คงเดิม) ...
