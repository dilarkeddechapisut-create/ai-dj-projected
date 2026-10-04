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

# ==========================================
# 1. ตั้งค่าหน้าเพจ & CSS + Video Background
# ==========================================
st.set_page_config(page_title="AI DJ Mood Matcher Pro", page_icon="🎧", layout="wide")

BG_VIDEO_URL = "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_083109_283f3553-e28f-428b-a723-d639c617eb2b.mp4"

st.markdown(f"""
<style>
    /* พื้นหลังหลักโปร่งใสเพื่อมองเห็นวิดีโอด้านหลัง */
    .stApp {{
        background: transparent !important;
        color: #ffffff;
    }}

    /* ซ่อนแถบดำและตั้งค่า iframe ของระบบอัดเสียงให้โปร่งใส */
    iframe,
    iframe[title="streamlit_mic_recorder.speech_to_text"],
    div[data-testid="stCustomComponentV1"],
    div[data-testid="stElementContainer"]:has(iframe) {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* วิดีโอ Background เต็มจอ */
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
        filter: brightness(0.32);
    }}

    /* ------------------------------------------ */
    /* Spotify Top-Center Pill Navigation Switcher */
    /* ------------------------------------------ */
    .top-nav-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 25px;
        margin-top: -10px;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 12px !important;
        background-color: rgba(18, 18, 18, 0.75);
        padding: 8px 16px;
        border-radius: 30px;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        width: fit-content;
        margin: 0 auto;
    }}

    div[data-testid="stRadio"] label {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        padding: 6px 18px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.25s ease-in-out !important;
        cursor: pointer !important;
        border: none !important;
    }}

    div[data-testid="stRadio"] label:hover {{
        background-color: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-1px);
    }}

    div[data-testid="stRadio"] label[data-checked="true"] {{
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p {{
        font-size: 0.95rem !important;
    }}

    /* ซ่อนจุดวงกลม Radio Default */
    div[data-testid="stRadio"] input[type="radio"] {{
        display: none !important;
    }}

    /* ------------------------------------------ */
    /* Spotify Grid Cards Design (หน้าสำรวจเพลง)  */
    /* ------------------------------------------ */
    .spotify-card {{
        background-color: rgba(24, 24, 24, 0.85);
        border-radius: 12px;
        padding: 14px;
        transition: all 0.3s ease;
        position: relative;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }}
    .spotify-card:hover {{
        background-color: rgba(40, 40, 40, 0.95);
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.6);
    }}
    .spotify-card-img-wrapper {{
        position: relative;
        width: 100%;
        padding-top: 100%;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 12px;
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
        font-size: 1rem;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
    }}
    .spotify-card-subtitle {{
        font-size: 0.85rem;
        color: #b3b3b3;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 8px;
    }}
    .spotify-tag {{
        display: inline-block;
        background: rgba(29, 185, 84, 0.2);
        color: #1DB954;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 8px;
    }}

    /* ตกแต่ง Header */
    .main-header {{
        text-align: center;
        margin-top: 5px;
        margin-bottom: 15px;
    }}
    .main-header h1 {{
        font-size: 2.2rem;
        font-weight: 800;
        color: #1DB954;
        margin-bottom: 4px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.8);
    }}

    /* Floating Player Box */
    div[data-key="floating_player_box"],
    div.st-key-floating_player_box,
    div[class*="st-key-floating_player_box"],
    div[data-testid="stVerticalBlock"]:has(> div > div > div.floating-marker) {{
        position: fixed !important;
        bottom: 25px !important;
        right: 25px !important;
        width: 350px !important;
        max-width: calc(100vw - 40px) !important;
        background: #121212 !important;
        border: 1.5px solid #1DB954 !important;
        border-radius: 16px !important;
        padding: 12px 14px 10px 14px !important;
        z-index: 999999 !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8) !important;
    }}
</style>

<!-- HTML Tag วิดีโอพื้นหลัง -->
<video autoplay loop muted playsinline id="bg-video">
    <source src="{BG_VIDEO_URL}" type="video/mp4">
</video>
""", unsafe_allow_html=True)

# ==========================================
# 2. State Management
# ==========================================
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
# 3. Header & Top-Center Spotify Nav Switcher
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>🎧 AI DJ Mood Matcher Pro</h1>
</div>
""", unsafe_allow_html=True)

# ปุ่มสลับหน้าอยู่ด้านบนตรงกลาง (Spotify Pills Style)
nav_choice = st.radio(
    "Navigation",
    ["🎧 AI DJ Studio", "🎵 สำรวจเพลงตามอารมณ์", "📊 สถิติ & วิเคราะห์", "❤️ เพลงโปรด & ประวัติ"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

# ==========================================
# 4. Mock Data สำหรับหน้า "สำรวจเพลงตามอารมณ์"
# ==========================================
MOOD_PRESETS = {
    "☕ ชิลล์ & ทำงาน (Focus & Chill)": [
        {"name": "Sunflower", "artist": "Post Malone, Swae Lee", "tag": "Lofi / Chill", "cover": "https://i.scdn.co/image/ab67616d0000b273e2e352d89826aef6dbd5ff8f", "preview": "https://p.scdn.co/mp3-preview/38072ebf3f721c569f6e1f0e428e2171545625bf"},
        {"name": "Lofi Study Beats", "artist": "Chillhop Music", "tag": "Focus Beats", "cover": "https://i.scdn.co/image/ab67616d0000b273b5f00e93297a768f44d18306", "preview": "https://p.scdn.co/mp3-preview/a6e9a66d0c75c58bc39b98ec35a09e0750766b1e"},
        {"name": "Coffee Shop Vibes", "artist": "Acoustic Morning", "tag": "Acoustic", "cover": "https://i.scdn.co/image/ab67616d0000b27341e411b9319808a5433a0117", "preview": None},
        {"name": "Night Trouble", "artist": "Petit Biscuit", "tag": "Chill Electronic", "cover": "https://i.scdn.co/image/ab67616d0000b2732a39a03975c3f858277be0c5", "preview": None}
    ],
    "🌧️ ฝนตก & เหงา (Rainy Mood)": [
        {"name": "Glimpse of Us", "artist": "Joji", "tag": "Sad Ballad", "cover": "https://i.scdn.co/image/ab67616d0000b273014101e469d727b1f516a570", "preview": "https://p.scdn.co/mp3-preview/0d3c631a7894d036e78864f13fb2d1e02ef29b87"},
        {"name": "พิง", "artist": "NONT TANONT", "tag": "Thai Pop", "cover": "https://i.scdn.co/image/ab67616d0000b2737a30ef1d22754e3edc41fa2a", "preview": None},
        {"name": "ฝนตกไหม", "artist": "Three Man Down", "tag": "Indie Rock", "cover": "https://i.scdn.co/image/ab67616d0000b273cb69ec1dfbe39d4825d194cf", "preview": None},
        {"name": "คำถามซึ่งไร้คนตอบ", "artist": "Getsunova", "tag": "Thai Pop", "cover": "https://i.scdn.co/image/ab67616d0000b273d40a2fdf2edc93e43dd59d24", "preview": None}
    ],
    "🔥 พลังงานสูง & ออกกำลังกาย (Workout)": [
        {"name": "Blinding Lights", "artist": "The Weeknd", "tag": "Synthwave", "cover": "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b5d718688e", "preview": "https://p.scdn.co/mp3-preview/3e10419131d96e511737e6f6a7350730d1d2b861"},
        {"name": "Levitating", "artist": "Dua Lipa", "tag": "Dance Pop", "cover": "https://i.scdn.co/image/ab67616d0000b27329d2f2d9c4c51921f66a2e92", "preview": None},
        {"name": "Stronger", "artist": "Kanye West", "tag": "Hip-Hop", "cover": "https://i.scdn.co/image/ab67616d0000b2732626e25501869e5d4e782e44", "preview": None},
        {"name": "วัดปะหล่ะ?", "artist": "4EVE", "tag": "T-Pop Energy", "cover": "https://i.scdn.co/image/ab67616d0000b2732ef6dbf32bbd74f26b527581", "preview": None}
    ],
    "💖 ความรัก & อบอุ่น (Romantic Vibes)": [
        {"name": "Perfect", "artist": "Ed Sheeran", "tag": "Acoustic Pop", "cover": "https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96", "preview": None},
        {"name": "Until I Found You", "artist": "Stephen Sanchez", "tag": "Retro Love", "cover": "https://i.scdn.co/image/ab67616d0000b2735233c3066373b9e4a3627f12", "preview": None},
        {"name": "รักแรก (First Love)", "artist": "NONT TANONT", "tag": "Thai Ballad", "cover": "https://i.scdn.co/image/ab67616d0000b27376c6dd3a097d6fb3a1e0b57e", "preview": None},
        {"name": "Double Take", "artist": "dhruv", "tag": "R&B / Soul", "cover": "https://i.scdn.co/image/ab67616d0000b27339735d64235e26bbf117d337", "preview": None}
    ]
}

# ==========================================
# 5. การแสดงผลตามหน้าที่เลือก (Pages)
# ==========================================

# ------------------------------------------
# PAGE 1: 🎧 AI DJ STUDIO (หน้าสร้าง & จัดเพลง)
# ------------------------------------------
if nav_choice == "🎧 AI DJ Studio":
    st.markdown("### 🎙️ 1. เล่าความรู้สึก หรือเลือกอารมณ์ด่วน")

    # ปุ่มเลือกอารมณ์ด่วน (Quick Mood Chips)
    q_col1, q_col2, q_col3, q_col4, q_col5, q_col6 = st.columns(6)
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

    # ปุ่มพูดด้วยเสียง (Speech to Text)
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

    # ช่องกรอกข้อความหลัก
    mood_text = st.text_area(
        "ความรู้สึกของคุณ:",
        value=st.session_state.user_input_text,
        placeholder="เช่น วันนี้เลิกงานแล้ว เหนื่อยมากๆ อยากหาเพลงชิลๆ ฟังผ่อนคลาย...",
        height=100,
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
                    st.session_state.ai_message = ai_result['encouragement']
                    valid_tracks = []
                    
                    for song in ai_result['songs']:
                        try:
                            track_info = search_spotify_track(song['title'], song['artist'])
                        except:
                            track_info = None

                        img_url, preview_url, full_url = get_track_preview(song['title'], song['artist'])
                        
                        if not track_info:
                            track_info = {
                                'name': song['title'],
                                'artist': song['artist'],
                                'album_cover': img_url if img_url else "https://via.placeholder.com/500?text=No+Cover",
                                'preview_url': preview_url,
                                'spotify_url': full_url if full_url else "#"
                            }
                        else:
                            if preview_url: track_info['preview_url'] = preview_url
                            if img_url: track_info['album_cover'] = img_url
                            if not track_info.get('spotify_url') and full_url: track_info['spotify_url'] = full_url
                        
                        if track_info:
                            track_info['reason'] = song['reason']
                            valid_tracks.append(track_info)
                    
                    st.session_state.playlist = valid_tracks
                    st.session_state.current_track_index = 0
                    
                    # บันทึกลง History
                    st.session_state.history.insert(0, {
                        'time': datetime.now().strftime("%H:%M - %d/%m/%Y"),
                        'mood': mood_text,
                        'persona': dj_persona,
                        'playlist': valid_tracks,
                        'message': ai_result['encouragement']
                    })
        else:
            st.warning("⚠️ กรุณาพิมพ์หรือเลือกความรู้สึกของคุณก่อนครับ")

    # แสดงผล Playlist
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
                
                # ปุ่มฟังตัวอย่าง & Fav
                btn_c1, btn_c2, btn_c3 = st.columns([1.2, 0.8, 1])
                with btn_c1:
                    if track_info.get('preview_url'):
                        if st.button(f"▶️ ฟังตัวอย่าง", key=f"play_dj_{i}", use_container_width=True):
                            st.session_state.current_preview_url = track_info['preview_url']
                            st.session_state.current_track_name = track_info['name']
                            st.session_state.current_track_index = i
                            st.rerun()
                    else:
                        st.button("❌ ไม่มีตัวอย่าง", key=f"noplay_dj_{i}", disabled=True, use_container_width=True)
                
                with btn_c2:
                    is_fav = any(f['name'] == track_info['name'] for f in st.session_state.favorites)
                    if st.button("❤️" if is_fav else "🤍", key=f"fav_dj_{i}", use_container_width=True):
                        if is_fav:
                            st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != track_info['name']]
                        else:
                            st.session_state.favorites.append(track_info)
                        st.rerun()

                with btn_c3:
                    st.link_button("🟢 Spotify", track_info.get('spotify_url', '#'), use_container_width=True)

# ------------------------------------------
# PAGE 2: 🎵 สำรวจเพลงตามอารมณ์ (หน้าใหม่ SPOTIFY GRID)
# ------------------------------------------
elif nav_choice == "🎵 สำรวจเพลงตามอารมณ์":
    st.subheader("🎵 สำรวจเพลงตามหมวดหมู่อารมณ์ (Spotify Visual Grid)")
    st.caption("เลือกฟีลลิ่งของคุณเพื่อค้นพบเพลงเด็ดๆ พร้อมกดฟังตัวอย่างเพลงได้ทันที")

    selected_mood = st.selectbox(
        "🎯 เลือกหมวดหมู่อารมณ์ที่ต้องการค้นหา:",
        list(MOOD_PRESETS.keys())
    )

    st.markdown(f"#### 📂 เพลงในหมวดหมู่: `{selected_mood}`")
    
    songs_in_mood = MOOD_PRESETS[selected_mood]
    
    # แสดงผลเป็น Grid 4 คอลัมน์ต่อแถว แบบ Spotify UI
    grid_cols = st.columns(4)
    
    for idx, song in enumerate(songs_in_mood):
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
                    if st.button("▶️ เล่นตัวอย่าง", key=f"grid_play_{selected_mood}_{idx}", use_container_width=True):
                        st.session_state.current_preview_url = song['preview']
                        st.session_state.current_track_name = song['name']
                        st.rerun()
                else:
                    st.button("🔇 ไม่มีตัวอย่าง", key=f"grid_noplay_{selected_mood}_{idx}", disabled=True, use_container_width=True)
            
            with p_col2:
                is_fav = any(f['name'] == song['name'] for f in st.session_state.favorites)
                if st.button("❤️ เพิ่มแล้ว" if is_fav else "🤍 เก็บไว้", key=f"grid_fav_{selected_mood}_{idx}", use_container_width=True):
                    if is_fav:
                        st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != song['name']]
                    else:
                        st.session_state.favorites.append({
                            'name': song['name'],
                            'artist': song['artist'],
                            'album_cover': song['cover'],
                            'preview_url': song.get('preview'),
                            'reason': f"เพลงแนะนำจากหมวด {selected_mood}"
                        })
                    st.rerun()

# ------------------------------------------
# PAGE 3: 📊 สถิติ & บทวิเคราะห์ (ANALYTICS)
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
        except:
            st.info("ระบบกำลังประมวลผลแผนภูมิสถิติ...")
    else:
        st.info("💡 สร้างเพลย์ลิสต์ในหน้า 'AI DJ Studio' ก่อน เพื่อดูการวิเคราะห์สถิติอารมณ์เพลง")

# ------------------------------------------
# PAGE 4: ❤️ เพลงโปรด & ประวัติ (FAVORITES & HISTORY)
# ------------------------------------------
elif nav_choice == "❤️️ เพลงโปรด & ประวัติ":
    st.subheader("❤️ เพลงโปรดที่คุณบันทึกไว้")
    if len(st.session_state.favorites) > 0:
        fav_cols = st.columns(3)
        for idx, fav_track in enumerate(st.session_state.favorites):
            with fav_cols[idx % 3]:
                st.markdown(f"""
                <div class="spotify-card">
                    <div class="spotify-card-img-wrapper">
                        <img src="{fav_track.get('album_cover', 'https://via.placeholder.com/300')}" class="spotify-card-img">
                    </div>
                    <div class="spotify-card-title">{fav_track['name']}</div>
                    <div class="spotify-card-subtitle">{fav_track['artist']}</div>
                </div>
                """, unsafe_allow_html=True)
                if fav_track.get('preview_url'):
                    if st.button("▶️ ฟังเพลงนี้", key=f"fav_play_page_{idx}", use_container_width=True):
                        st.session_state.current_preview_url = fav_track['preview_url']
                        st.session_state.current_track_name = fav_track['name']
                        st.rerun()
    else:
        st.caption("ยังไม่มีเพลงโปรด กดหัวใจ ❤️ ที่การ์ดเพลงในหน้าต่างๆ เพื่อเพิ่มไว้ที่นี่ได้เลย")

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

# ==========================================
# 6. Floating Player (เล่นเพลงตัวอย่างลอยด้านล่าง)
# ==========================================
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
