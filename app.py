import streamlit as st
import time
from datetime import datetime
from streamlit_mic_recorder import speech_to_text

# นำเข้า Service ต่างๆ
from ai_service import get_playlist_from_ai
from spotify_service import search_spotify_track
from stats_service import create_radar_chart
from feedback_service import save_feedback
from preview_service import get_track_preview
from auth_service import (
    sign_in_with_email_and_password, 
    sign_up_with_email_and_password, 
    reset_password
)

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="AI DJ Mood Matcher Pro",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BG_VIDEO_URL = "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_083109_283f3553-e28f-428b-a723-d639c617eb2b.mp4"

# ==========================================
# 2. Liquid Glass & Responsive CSS
# ==========================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Prompt', sans-serif;
    }}

    .stApp {{
        background-color: #121212 !important;
        color: #ffffff;
    }}

    #bg-video {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: -100;
        object-fit: cover;
        filter: brightness(0.35);
    }}

    iframe,
    iframe[title="streamlit_mic_recorder.speech_to_text"],
    div[data-testid="stCustomComponentV1"],
    div[data-testid="stElementContainer"]:has(iframe) {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    div.stButton > button {{
        background: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.25s ease-in-out !important;
        width: 100% !important;
    }}

    div.stButton > button:hover {{
        background: rgba(255, 255, 255, 0.28) !important;
        border-color: rgba(255, 255, 255, 0.55) !important;
        box-shadow: 0 10px 35px 0 rgba(29, 185, 84, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px);
        color: #ffffff !important;
    }}

    div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, rgba(29, 185, 84, 0.85), rgba(20, 140, 60, 0.95)) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 25px rgba(29, 185, 84, 0.4) !important;
    }}

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
    }}

    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {{
        color: #ffffff !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 10px !important;
        background: rgba(18, 18, 18, 0.65);
        backdrop-filter: blur(16px);
        padding: 8px 16px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        width: fit-content;
        margin: 0 auto;
    }}

    div[data-testid="stRadio"] label {{
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        padding: 8px 18px !important;
        font-weight: 500 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}

    div[data-testid="stRadio"] label[data-checked="true"] {{
        background: #1DB954 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stRadio"] input[type="radio"] {{
        display: none !important;
    }}

    .spotify-card {{
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
    }}

    .spotify-card-img-wrapper {{
        position: relative;
        width: 100%;
        padding-top: 100%;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 10px;
        background-color: #222;
    }}

    .spotify-card-img {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}

    .spotify-card-title {{
        font-weight: 700;
        font-size: 0.95rem;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .spotify-card-subtitle {{
        font-size: 0.82rem;
        color: #b3b3b3;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .spotify-tag {{
        display: inline-block;
        background: rgba(29, 185, 84, 0.25);
        color: #1DB954;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 10px;
        margin-bottom: 6px;
    }}

    .main-header {{
        text-align: center;
        margin-top: 5px;
        margin-bottom: 15px;
    }}

    .main-header h1 {{
        font-size: 2.2rem;
        font-weight: 800;
        color: #1DB954;
        text-shadow: 0 4px 15px rgba(0, 0, 0, 0.7);
    }}

    .auth-container {{
        max-width: 420px;
        margin: 40px auto;
        padding: 30px;
        background: rgba(18, 18, 18, 0.75);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }}

    .user-badge {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 6px 16px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-size: 0.88rem;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }}
</style>

<video autoplay loop muted playsinline id="bg-video">
    <source src="{BG_VIDEO_URL}" type="video/mp4">
</video>
""", unsafe_allow_html=True)

# ==========================================
# 3. State Management
# ==========================================
if 'user' not in st.session_state:
    st.session_state.user = None
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'ai_message' not in st.session_state:
    st.session_state.ai_message = ""
if 'current_preview_url' not in st.session_state:
    st.session_state.current_preview_url = None
if 'current_track_name' not in st.session_state:
    st.session_state.current_track_name = ""
if 'current_track_index' not in st.session_state:
    st.session_state.current_track_index = 0
if 'user_input_text' not in st.session_state:
    st.session_state.user_input_text = ""
if 'last_mic_text' not in st.session_state:
    st.session_state.last_mic_text = ""
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'history' not in st.session_state:
    st.session_state.history = []

# ==========================================
# 4. Helper Functions
# ==========================================
@st.cache_data(ttl=3600)
def fetch_live_track_info(title, artist, tag):
    try:
        track_info = search_spotify_track(title, artist)
    except Exception:
        track_info = None

    try:
        img_url, preview_url, full_url = get_track_preview(title, artist)
    except Exception:
        img_url, preview_url, full_url = None, None, None

    fallback_img = "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400&auto=format&fit=crop&q=80"
    
    cover = img_url if img_url else (track_info.get('album_cover') if track_info else fallback_img)
    preview = preview_url if preview_url else (track_info.get('preview_url') if track_info else None)
    spotify_link = full_url if full_url else (track_info.get('spotify_url') if track_info else f"https://open.spotify.com/search/{title}%20{artist}")

    return {
        "name": title,
        "artist": artist,
        "tag": tag,
        "cover": cover,
        "preview": preview,
        "spotify_url": spotify_link
    }

def handle_like_song(track, mood_prompt=""):
    is_fav = any(f['name'] == track['name'] for f in st.session_state.favorites)
    user_email = st.session_state.user.get('email', '') if st.session_state.user else ''
    
    if is_fav:
        st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != track['name']]
        st.toast(f"ลบ {track['name']} ออกจากรายการโปรดแล้ว", icon="🗑️")
    else:
        st.session_state.favorites.append(track)
        try:
            current_mood = mood_prompt or st.session_state.user_input_text or "กดถูกใจจากรายการแนะนำ"
            save_feedback(
                mood_text=f"[{user_email}] {current_mood}" if user_email else current_mood,
                song_name=track['name'],
                artist=track.get('artist', ''),
                is_liked=True
            )
            st.toast(f"เพิ่ม {track['name']} ในเพลงโปรดเรียบร้อย! 💖", icon="✅")
        except Exception:
            st.toast(f"เพิ่ม {track['name']} ในเพลงโปรดแล้ว", icon="❤️")

# ==========================================
# 5. Firebase Authentication View (หน้าเข้าสู่ระบบ)
# ==========================================
if st.session_state.user is None:
    st.markdown("""
    <div class="main-header">
        <h1>🎧 AI DJ Mood Matcher Pro</h1>
        <p style="color: #bbb;">กรุณาเข้าสู่ระบบด้วย Firebase ก่อนเริ่มใช้งาน</p>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
    
    with auth_col2:
        auth_mode = st.tabs(["🔐 เข้าสู่ระบบ", "📝 สมัครสมาชิก", "🔑 ลืมรหัสผ่าน"])
        
        # TAB 1: เข้าสู่ระบบ
        with auth_mode[0]:
            st.subheader("เข้าสู่ระบบ")
            login_email = st.text_input("อีเมล", key="login_email_input", placeholder="your_email@gmail.com")
            login_pass = st.text_input("รหัสผ่าน", type="password", key="login_pass_input")
            
            if st.button("🚀 เข้าสู่ระบบ", type="primary", use_container_width=True, key="login_btn"):
                if login_email and login_pass:
                    with st.spinner("กำลังตรวจสอบข้อมูล..."):
                        res = sign_in_with_email_and_password(login_email, login_pass)
                        if res["success"]:
                            st.session_state.user = res["info"]
                            st.success("เข้าสู่ระบบสำเร็จ!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(res["error"])
                else:
                    st.warning("กรุณากรอกอีเมลและรหัสผ่านให้ครบถ้วน")

        # TAB 2: สมัครสมาชิก
        with auth_mode[1]:
            st.subheader("สร้างบัญชีใหม่")
            signup_email = st.text_input("อีเมลสำหรับสมัคร", key="signup_email_input", placeholder="your_email@gmail.com")
            signup_pass = st.text_input("รหัสผ่าน (อย่างน้อย 6 ตัวอักษร)", type="password", key="signup_pass_input")
            signup_confirm = st.text_input("ยืนยันรหัสผ่าน", type="password", key="signup_confirm_input")
            
            if st.button("✨ สมัครสมาชิก", type="primary", use_container_width=True, key="signup_btn"):
                if signup_email and signup_pass and signup_confirm:
                    if signup_pass != signup_confirm:
                        st.error("รหัสผ่านทั้งสองช่องไม่ตรงกัน")
                    else:
                        with st.spinner("กำลังสร้างบัญชีผู้ใช้..."):
                            res = sign_up_with_email_and_password(signup_email, signup_pass)
                            if res["success"]:
                                st.session_state.user = res["info"]
                                st.success("สมัครสมาชิกสำเร็จและเข้าสู่ระบบเรียบร้อย!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(res["error"])
                else:
                    st.warning("กรุณากรอกข้อมูลให้ครบทุกช่อง")

        # TAB 3: ลืมรหัสผ่าน
        with auth_mode[2]:
            st.subheader("รีเซ็ตรหัสผ่าน")
            reset_email_input = st.text_input("กรอกอีเมลของคุณ", key="reset_email_input")
            
            if st.button("📧 ส่งลิงก์รีเซ็ตรหัสผ่าน", use_container_width=True, key="reset_btn"):
                if reset_email_input:
                    with st.spinner("กำลังส่งอีเมล..."):
                        res = reset_password(reset_email_input)
                        if res["success"]:
                            st.success("ส่งลิงก์รีเซ็ตรหัสผ่านไปยังอีเมลของคุณเรียบร้อยแล้ว โปรดตรวจสอบใน กล่องข้อความ/Junk Mail")
                        else:
                            st.error(res["error"])
                else:
                    st.warning("กรุณากรอกอีเมล")

    st.stop() # หยุดการทำงานไม่ให้เล่นส่วนแอปถ้ายังไม่ Login

# ==========================================
# 6. Main App Content (หลังเข้าสู่ระบบแล้ว)
# ==========================================

# Top User Bar Header
top_c1, top_c2 = st.columns([3, 1])
with top_c1:
    st.markdown(f"""
    <div class="main-header" style="text-align: left; margin-bottom: 0;">
        <h1 style="font-size: 1.8rem; margin:0;">🎧 AI DJ Mood Matcher Pro</h1>
    </div>
    """, unsafe_allow_html=True)

with top_c2:
    user_email = st.session_state.user.get('email', 'User')
    st.markdown(f"<div class='user-badge'>👤 {user_email}</div>", unsafe_allow_html=True)
    if st.button("🚪 ออกจากระบบ", key="logout_btn"):
        st.session_state.user = None
        st.session_state.playlist = []
        st.session_state.favorites = []
        st.rerun()

st.write("")

nav_choice = st.radio(
    "Navigation",
    ["🎧 AI DJ Studio", "🎵 สำรวจเพลงตามอารมณ์", "📊 สถิติ & วิเคราะห์", "❤️ เพลงโปรด & ประวัติ"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

MOOD_PRESETS_SEEDS = {
    "☕ ชิลล์ & ทำงาน (Focus & Chill)": [
        {"title": "Sunflower", "artist": "Post Malone", "tag": "Lofi / Chill"},
        {"title": "Best Part", "artist": "Daniel Caesar", "tag": "Acoustic R&B"},
        {"title": "ดวงใจ", "artist": "PALMY", "tag": "Chill Pop"},
        {"title": "Night Trouble", "artist": "Petit Biscuit", "tag": "Electronic Chill"}
    ],
    "🌧️ ฝนตก & เหงา (Rainy Mood)": [
        {"title": "Glimpse of Us", "artist": "Joji", "tag": "Sad Ballad"},
        {"title": "พิง", "artist": "NONT TANONT", "tag": "Thai Pop"},
        {"title": "ฝนตกไหม", "artist": "Three Man Down", "tag": "Indie Rock"},
        {"title": "คำถามซึ่งไร้คนตอบ", "artist": "Getsunova", "tag": "Pop Rock"}
    ],
    "🔥 พลังงานสูง & ออกกำลังกาย (Workout)": [
        {"title": "Blinding Lights", "artist": "The Weeknd", "tag": "Synthwave"},
        {"title": "Levitating", "artist": "Dua Lipa", "tag": "Dance Pop"},
        {"title": "Stronger", "artist": "Kanye West", "tag": "Hip-Hop"},
        {"title": "วัดปะหล่ะ?", "artist": "4EVE", "tag": "T-Pop Energy"}
    ],
    "💖 ความรัก & อบอุ่น (Romantic Vibes)": [
        {"title": "Perfect", "artist": "Ed Sheeran", "tag": "Acoustic Pop"},
        {"title": "Until I Found You", "artist": "Stephen Sanchez", "tag": "Retro Love"},
        {"title": "รักแรก", "artist": "NONT TANONT", "tag": "Thai Ballad"},
        {"title": "Double Take", "artist": "dhruv", "tag": "R&B / Soul"}
    ]
}

# ------------------------------------------
# PAGE 1: 🎧 AI DJ STUDIO
# ------------------------------------------
if nav_choice == "🎧 AI DJ Studio":
    st.markdown("### 🎙️ 1. เล่าความรู้สึก หรือเลือกอารมณ์ด่วน")

    q_col1, q_col2, q_col3, q_col4, q_col5, q_col6 = st.columns([1, 1, 1, 1, 1, 1])
    if q_col1.button("💻 โฟกัสทำงาน", use_container_width=True):
        st.session_state.user_input_text = "กำลังนั่งทำงาน อยากได้เพลงเคลียร์สมอง ช่วยให้มีสมาธิยาวๆ"
    if q_col2.button("☕ ชิลล์วันหยุด", use_container_width=True):
        st.session_state.user_input_text = "วันหยุดสบายๆ จิบกาแฟ อยากฟังเพลง Acoustic/Lofi ชิลๆ"
    if q_col3.button("🚗 ขับรถเที่ยว", use_container_width=True):
        st.session_state.user_input_text = "กำลังขับรถเดินทางไกล อยากได้เพลงฟังเพลินๆ จังหวะกลางๆ"
    if q_col4.button("💪 ออกกำลังกาย", use_container_width=True):
        st.session_state.user_input_text = "กำลังจะเข้าฟิตเนส ขอเพลงบีตหนักๆ พลังงานสูง ช่วยปลุกไฟ"
    if q_col5.button("🌧️ ฝนตกเหงาๆ", use_container_width=True):
        st.session_state.user_input_text = "บรรยากาศฝนตก เหงาๆ อยากฟังเพลงอินดี้เศร้าๆ ดึงอารมณ์นิดนึง"
    if q_col6.button("💔 อกหักรักพัง", use_container_width=True):
        st.session_state.user_input_text = "เพิ่งเลิกกับแฟน เสียใจมาก ขอเพลงเศร้าตอกย้ำอารมณ์คนอกหัก"

    text_from_mic = speech_to_text(
        language='th-TH', 
        start_prompt="🎙️ กดเพื่อพูดความรู้สึก", 
        stop_prompt="🛑 กดเพื่อหยุดการอัด", 
        just_once=False,
        key='STT'
    )

    if text_from_mic and text_from_mic != st.session_state.last_mic_text:
        st.session_state.user_input_text = text_from_mic
        st.session_state.last_mic_text = text_from_mic

    mood_text = st.text_area(
        "ความรู้สึกของคุณ:",
        value=st.session_state.user_input_text,
        placeholder="เช่น วันนี้เลิกงานแล้ว เหนื่อยมากๆ อยากหาเพลงชิลๆ ฟังผ่อนคลาย...",
        height=90,
        label_visibility="collapsed"
    )

    st.markdown("### ⚙️ 2. ปรับแต่งสไตล์ AI DJ")
    col_p1, col_p2, col_p3 = st.columns([1.2, 1, 1])
    
    with col_p1:
        dj_persona = st.selectbox(
            "🎭 เลือกคาแรกเตอร์ AI DJ:",
            ["พี่ดีเจสายอบอุ่นปลอบใจ 💖", "ดีเจสายฮา/กวนๆ 🤪", "ดีเจอินดี้สายติสท์ 🎨", "ดีเจสายสร้างพลังใจ 🔥"]
        )
    with col_p2:
        energy_level = st.select_slider(
            "⚡ ระดับพลังงานเพลง:",
            options=["ผ่อนคลาย 😴", "ปานกลาง 😊", "สูงจัดเต็ม ⚡"],
            value="ปานกลาง 😊"
        )
    with col_p3:
        num_songs = st.slider("🎵 จำนวนเพลง:", min_value=3, max_value=12, value=5)

    if st.button("✨ ให้ AI DJ จัดเพลงให้ทันที", type="primary", use_container_width=True):
        if mood_text:
            with st.spinner("AI กำลังสวมบทบาท DJ และคัดสรรเพลย์ลิสต์..."):
                augmented_prompt = f"[สไตล์ DJ: {dj_persona}] [ระดับพลังงานเพลง: {energy_level}] ความรู้สึกผู้ใช้: {mood_text}"
                ai_result = get_playlist_from_ai(augmented_prompt, num_songs)
                
                if ai_result:
                    st.session_state.ai_message = ai_result.get('encouragement', '')
                    valid_tracks = []
                    
                    for song in ai_result.get('songs', []):
                        track_data = fetch_live_track_info(song['title'], song['artist'], dj_persona)
                        track_info = {
                            'name': song['title'],
                            'artist': song['artist'],
                            'album_cover': track_data['cover'],
                            'preview_url': track_data['preview'],
                            'spotify_url': track_data['spotify_url'],
                            'reason': song.get('reason', '')
                        }
                        valid_tracks.append(track_info)
                    
                    st.session_state.playlist = valid_tracks
                    st.session_state.current_track_index = 0
                    
                    st.session_state.history.insert(0, {
                        'time': datetime.now().strftime("%H:%M - %d/%m/%Y"),
                        'mood': mood_text,
                        'persona': dj_persona,
                        'playlist': valid_tracks,
                        'message': ai_result.get('encouragement', '')
                    })
        else:
            st.warning("⚠️ กรุณาพิมพ์หรือเลือกความรู้สึกของคุณก่อนครับ")

    if len(st.session_state.playlist) > 0:
        st.success("🎉 จัดเพลย์ลิสต์เสร็จเรียบร้อย!")
        st.markdown(f"### 💌 ข้อความจาก {dj_persona}:\n> *{st.session_state.ai_message}*")
        
        cols = st.columns(3)
        for i, track_info in enumerate(st.session_state.playlist):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="spotify-card">
                    <div class="spotify-card-img-wrapper">
                        <img src="{track_info['album_cover']}" class="spotify-card-img" alt="Cover">
                    </div>
                    <div class="spotify-card-title">{track_info['name']}</div>
                    <div class="spotify-card-subtitle">{track_info['artist']}</div>
                    <div style="font-size:0.8rem; color:#aaa; font-style:italic;">{track_info.get('reason', '')[:60]}...</div>
                </div>
                """, unsafe_allow_html=True)
                
                btn_c1, btn_c2, btn_c3 = st.columns([1.2, 0.8, 1])
                with btn_c1:
                    if track_info.get('preview_url'):
                        if st.button("▶️ ฟังตัวอย่าง", key=f"play_dj_{i}", use_container_width=True):
                            st.session_state.current_preview_url = track_info['preview_url']
                            st.session_state.current_track_name = track_info['name']
                            st.session_state.current_track_index = i
                            st.rerun()
                    else:
                        st.button("🔇 ไม่มีเสียง", key=f"noplay_dj_{i}", disabled=True, use_container_width=True)
                
                with btn_c2:
                    is_fav = any(f['name'] == track_info['name'] for f in st.session_state.favorites)
                    if st.button("❤️" if is_fav else "🤍", key=f"fav_dj_{i}", use_container_width=True):
                        handle_like_song(track_info, mood_prompt=mood_text)
                        st.rerun()

                with btn_c3:
                    st.link_button("🟢 Spotify", track_info.get('spotify_url', '#'), use_container_width=True)

# ------------------------------------------
# PAGE 2: 🎵 สำรวจเพลงตามอารมณ์
# ------------------------------------------
elif nav_choice == "🎵 สำรวจเพลงตามอารมณ์":
    st.subheader("🎵 สำรวจเพลงตามหมวดหมู่อารมณ์")
    selected_mood = st.selectbox("🎯 เลือกหมวดหมู่อารมณ์:", list(MOOD_PRESETS_SEEDS.keys()))

    seeds = MOOD_PRESETS_SEEDS[selected_mood]
    grid_cols = st.columns(4)
    
    for idx, seed in enumerate(seeds):
        song = fetch_live_track_info(seed['title'], seed['artist'], seed['tag'])
        
        with grid_cols[idx % 4]:
            st.markdown(f"""
            <div class="spotify-card">
                <div class="spotify-card-img-wrapper">
                    <img src="{song['cover']}" class="spotify-card-img" alt="Album Art">
                </div>
                <span class="spotify-tag">{song['tag']}</span>
                <div class="spotify-card-title">{song['name']}</div>
                <div class="spotify-card-subtitle">{song['artist']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            p_col1, p_col2 = st.columns([1.5, 1])
            with p_col1:
                if song.get('preview'):
                    if st.button("▶️ ฟังตัวอย่าง", key=f"grid_play_{selected_mood}_{idx}", use_container_width=True):
                        st.session_state.current_preview_url = song['preview']
                        st.session_state.current_track_name = song['name']
                        st.rerun()
                else:
                    st.button("🔇 ไม่มีตัวอย่าง", key=f"grid_noplay_{selected_mood}_{idx}", disabled=True, use_container_width=True)
            
            with p_col2:
                is_fav = any(f['name'] == song['name'] for f in st.session_state.favorites)
                if st.button("❤️" if is_fav else "🤍 เก็บไว้", key=f"grid_fav_{selected_mood}_{idx}", use_container_width=True):
                    track_dict = {
                        'name': song['name'],
                        'artist': song['artist'],
                        'album_cover': song['cover'],
                        'preview_url': song.get('preview'),
                        'spotify_url': song['spotify_url'],
                        'reason': f"เพลงแนะนำจากหมวด {selected_mood}"
                    }
                    handle_like_song(track_dict, mood_prompt=selected_mood)
                    st.rerun()

# ------------------------------------------
# PAGE 3: 📊 สถิติ & บทวิเคราะห์
# ------------------------------------------
elif nav_choice == "📊 สถิติ & วิเคราะห์":
    st.subheader("📈 วิเคราะห์สถิติอารมณ์ของ Playlist")
    if len(st.session_state.playlist) > 0:
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("จำนวนเพลงทั้งหมด", f"{len(st.session_state.playlist)} เพลง")
        m_col2.metric("สถานะ AI DJ", "พร้อมใช้งาน")
        m_col3.metric("เพลงที่มีไฟล์ตัวอย่าง", f"{sum(1 for t in st.session_state.playlist if t.get('preview_url'))} เพลง")

        try:
            fig = create_radar_chart(st.session_state.playlist)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("ระบบกำลังประมวลผลแผนภูมิสถิติ...")
    else:
        st.info("💡 สร้างเพลย์ลิสต์ในหน้า 'AI DJ Studio' ก่อน เพื่อดูการวิเคราะห์สถิติอารมณ์เพลง")

# ------------------------------------------
# PAGE 4: ❤️ เพลงโปรด & ประวัติ
# ------------------------------------------
elif nav_choice == "❤️ เพลงโปรด & ประวัติ":
    st.subheader("❤️ เพลงโปรดที่คุณบันทึกไว้")
    if len(st.session_state.favorites) > 0:
        fav_cols = st.columns(3)
        for idx, fav_track in enumerate(st.session_state.favorites):
            with fav_cols[idx % 3]:
                st.markdown(f"""
                <div class="spotify-card">
                    <div class="spotify-card-img-wrapper">
                        <img src="{fav_track.get('album_cover', 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400')}" class="spotify-card-img">
                    </div>
                    <div class="spotify-card-title">{fav_track['name']}</div>
                    <div class="spotify-card-subtitle">{fav_track['artist']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                f_col1, f_col2, f_col3 = st.columns([1.2, 0.8, 1])
                with f_col1:
                    if fav_track.get('preview_url'):
                        if st.button("▶️ ฟังเพลงนี้", key=f"fav_play_page_{idx}", use_container_width=True):
                            st.session_state.current_preview_url = fav_track['preview_url']
                            st.session_state.current_track_name = fav_track['name']
                            st.rerun()
                    else:
                        st.button("🔇 ไม่มีตัวอย่าง", key=f"fav_noplay_{idx}", disabled=True, use_container_width=True)
                
                with f_col2:
                    if st.button("🗑", key=f"fav_remove_{idx}", use_container_width=True):
                        handle_like_song(fav_track)
                        st.rerun()

                with f_col3:
                    st.link_button("🟢 Spotify", fav_track.get('spotify_url', '#'), use_container_width=True)
    else:
        st.caption("ยังไม่มีเพลงโปรด กดหัวใจ ❤️ ที่การ์ดเพลงในหน้าต่างๆ เพื่อเพิ่มไว้ที่นี่และบันทึกลง Sheet ได้เลย")

    st.divider()
    st.subheader("📜 ประวัติการจัดเพลย์ลิสต์ย้อนหลัง")
    if len(st.session_state.history) > 0:
        for item in st.session_state.history:
            with st.expander(f"🕒 {item['time']} | {item['mood'][:30]}..."):
                st.write(f"**คาแรกเตอร์:** {item['persona']}")
                st.write(f"**ข้อความ AI:** {item['message']}")
                for s in item['playlist']:
                    st.write(f"- {s['name']} - {s['artist']}")
    else:
        st.caption("ยังไม่มีประวัติการจัดเพลย์ลิสต์ในเซสชันนี้")

# Floating Audio Player Box
if st.session_state.current_preview_url:
    with st.container(key="floating_player_box"):
        st.markdown('<div class="floating-marker"></div>', unsafe_allow_html=True)
        
        head_c1, head_c2 = st.columns([85, 15])
        with head_c1:
            st.markdown(
                f"<div style='color:#1DB954; font-weight:bold; font-size:13px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>"
                f"🎵 กำลังเล่นตัวอย่าง: {st.session_state.current_track_name}</div>",
                unsafe_allow_html=True
            )
        with head_c2:
            if st.button("✖", key="close_player", use_container_width=True):
                st.session_state.current_preview_url = None
                st.session_state.current_track_name = ""
                st.rerun()

        st.audio(st.session_state.current_preview_url, format="audio/mp3", autoplay=True)
