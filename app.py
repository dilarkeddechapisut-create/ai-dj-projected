import streamlit as st

# ตั้งค่าหน้าจอแบบ Responsive
st.set_page_config(page_title="AI DJ Mood Matcher Pro", layout="wide", initial_sidebar_state="expanded")

# --- CSS สำหรับ Liquid Glass Style & Responsive Design ---
glass_css = """
<style>
/* นำเข้าฟอนต์เพื่อความสวยงาม */
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Prompt', sans-serif;
}

/* 1. ปุ่มทั่วไปสไตล์ Liquid Glass */
div.stButton > button {
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(16px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 16px !important;
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
    transition: all 0.3s ease-in-out !important;
    width: 100% !important;
    padding: 12px 20px !important;
    margin-bottom: 8px !important;
}

/* Hover & Active Effects บนปุ่ม Liquid Glass */
div.stButton > button:hover {
    background: rgba(255, 255, 255, 0.3) !important;
    border-color: rgba(255, 255, 255, 0.6) !important;
    box-shadow: 0 12px 40px 0 rgba(255, 255, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
    transform: translateY(-2px);
    color: #FFFFFF !important;
}

div.stButton > button:active {
    transform: translateY(1px);
}

/* 2. ช่องกรอกข้อมูล (Text Input, Textarea, Selectbox) สไตล์ Liquid Glass */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"] > div {
    background: rgba(255, 255, 255, 0.12) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 16px !important;
    color: #FFFFFF !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: #FFFFFF !important;
}

div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {
    color: rgba(255, 255, 255, 0.6) !important;
}

/* 3. การรองรับหน้าจอมือถือ (Mobile Responsive Design) */
@media (max-width: 768px) {
    div.stButton > button {
        padding: 10px 14px !important;
        font-size: 14px !important;
        border-radius: 12px !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-size: 1.3rem !important;
    }
}
</style>
"""

st.markdown(glass_css, unsafe_allow_html=True)
