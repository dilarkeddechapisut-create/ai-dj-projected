import streamlit as st
import time

# นำเข้า Service ต่างๆ
from ai_service import get_playlist_from_ai
from spotify_service import search_spotify_track
from stats_service import create_radar_chart
from feedback_service import save_feedback
from preview_service import get_track_preview

# ==========================================
# 1. ตั้งค่าหน้าเพจ & CSS
# ==========================================
st.set_page_config(page_title="AI DJ Mood Matcher", page_icon="🎧", layout="wide")

st.markdown("""
<style>
    /* พื้นหลัง Gradient */
    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: white;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Flip Card */
    .flip-card {
        background-color: transparent;
        width: 100%;
        height: 300px;
        perspective: 1000px;
        margin-bottom: 20px;
    }
    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s;
        transform-style: preserve-3d;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.5);
        border-radius: 15px;
    }
    .flip-card:hover .flip-card-inner {
        transform: rotateY(180deg);
    }
    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        border-radius: 15px;
    }
    .flip-card-front {
        background-color: #bbb;
        color: black;
    }
    .flip-card-front img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 15px;
    }
    .flip-card-back {
        background-color: #1DB954;
        color: white;
        transform: rotateY(180deg);
        padding: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* ==========================================
       Floating Player Container (ไร้แถบซ้อน + ลากขยับได้)
       ========================================== */
    div[data-testid="stVerticalBlock"] > div:has(div.floating-marker) {
        position: fixed !important;
        bottom: 30px !important;
        right: 25px !important;
        width: 360px !important;
        height: auto !important;
        background: #121212 !important;
        border: 1.5px solid #1DB954 !important;
        padding: 12px 14px 10px 14px !important;
        border-radius: 16px !important;
        z-index: 999999 !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8) !important;
    }

    /* ลบ Padding/Margin เกินของ Audio Player ตัวใน */
    div:has(div.floating-marker) div[data-testid="stAudio"] {
        margin: 4px 0px !important;
        padding: 0px !important;
    }

    div:has(div.floating-marker) audio {
        border-radius: 8px !important;
        width: 100% !important;
    }

    /* ตกแต่งปุ่มกดภายใน Floating Player */
    div:has(div.floating-marker) button {
        border-radius: 8px !important;
    }

    @media (max-width: 768px) {
        div[data-testid="stVerticalBlock"] > div:has(div.floating-marker) {
            bottom: 15px !important;
            right: 15px !important;
            left: 15px !important;
            width: calc(100vw - 30px) !important;
        }
    }
</style>
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

st.title("🎧 AI DJ: จัดเพลย์ลิสต์ตามความรู้สึก")
st.markdown("บอกความรู้สึกของคุณมาให้เราฟัง แล้ว AI จะจัดเพลงที่ใช่ให้คุณเอง!")

# ==========================================
# 3. ส่วน Input & เรียก AI
# ==========================================
col1, col2 = st.columns([2, 1])
with col1:
    mood_text = st.text_input("💬 พิมพ์ความรู้สึกของคุณที่นี่:", placeholder="เช่น วันนี้เหนื่อยจังเลย...")
    st.markdown("**หรือใช้ไมโครโฟนพูดความรู้สึก:**")
    audio_input = st.audio_input("พูดความรู้สึก") 
with col2:
    num_songs = st.slider("🎵 จำนวนเพลง", min_value=1, max_value=10, value=5)

if st.button("✨ ให้ AI จัดเพลย์ลิสต์", type="primary", use_container_width=True):
    if audio_input:
        st.info("กำลังประมวลผลเสียง... (ในเวอร์ชันนี้จะใช้ข้อความที่พิมพ์เป็นหลักก่อน)")
        
    if mood_text:
        with st.spinner("AI กำลังวิเคราะห์ความรู้สึกและค้นหาเพลง..."):
            ai_result = get_playlist_from_ai(mood_text, num_songs)
            
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
    else:
        st.warning("⚠️ กรุณาพิมพ์ความรู้สึกของคุณก่อนครับ")

# ==========================================
# 4. ส่วนแสดงผล
# ==========================================
if len(st.session_state.playlist) > 0:
    st.success("🎉 จัดเพลย์ลิสต์เสร็จเรียบร้อย!")
    st.markdown(f"### 💌 ข้อความจาก AI DJ:\n> *{st.session_state.ai_message}*")
    st.divider()
    
    cols = st.columns(3)
    for i, track_info in enumerate(st.session_state.playlist):
        with cols[i % 3]:
            # แสดง Card
            st.markdown(f"""
            <div class="flip-card">
                <div class="flip-card-inner">
                <div class="flip-card-front">
                    <img src="{track_info['album_cover']}" alt="Cover">
                </div>
                <div class="flip-card-back">
                    <h4>{track_info['name']}</h4>
                    <p>{track_info['artist']}</p>
                    <hr/>
                    <p style="font-size: 0.9em; font-style: italic;">{track_info.get('reason', '')}</p>
                </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ปุ่มฟังตัวอย่าง
            if track_info.get('preview_url'):
                if st.button(f"▶️ ฟังตัวอย่าง", key=f"play_{i}", use_container_width=True):
                    st.session_state.current_preview_url = track_info['preview_url']
                    st.session_state.current_track_name = track_info['name']
                    st.session_state.current_track_index = i
                    st.rerun() 
            else:
                st.button("❌ ไม่มีตัวอย่าง", key=f"no_play_{i}", disabled=True, use_container_width=True)
            
            # ปุ่มเปิดฟังบน Spotify
            st.link_button(
                "🟢 เปิดฟังบน Spotify", 
                track_info.get('spotify_url', '#'), 
                use_container_width=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📈 วิเคราะห์สถิติของ Playlist")
    try:
        fig = create_radar_chart(st.session_state.playlist)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("ไม่สามารถสร้างกราฟสถิติได้")

# ==========================================
# 5. Floating Player (ลากขยับได้ + ปุ่มเปลี่ยนเพลง)
# ==========================================
if st.session_state.current_preview_url and len(st.session_state.playlist) > 0:
    with st.container():
        st.markdown('<div class="floating-marker"></div>', unsafe_allow_html=True)
        
        curr_idx = st.session_state.get('current_track_index', 0)
        total_songs = len(st.session_state.playlist)
        
        # Header ของกล่อง สามารถคลิกลากย้ายตำแหน่งได้
        head_c1, head_c2 = st.columns([85, 15])
        with head_c1:
            st.markdown(
                f"<div id='drag-handle' style='cursor: move; user-select: none; color:#1DB954; font-weight:bold; font-size:13px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>"
                f"⠿ 🎵 {st.session_state.current_track_name} <span style='color:#888; font-size:11px;'>({curr_idx + 1}/{total_songs})</span></div>",
                unsafe_allow_html=True
            )
        with head_c2:
            if st.button("✖", key="close_player", use_container_width=True):
                st.session_state.current_preview_url = None
                st.session_state.current_track_name = ""
                st.rerun()

        # ตัวเล่นเสียง
        st.audio(st.session_state.current_preview_url, format="audio/mp3", autoplay=True)
        
        # ปุ่มควบคุม เล่นเพลงถัดไป / ย้อนกลับ
        ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([1, 1, 1])
        with ctrl_c1:
            if st.button("⏮️ ก่อนหน้า", key="prev_track", use_container_width=True):
                prev_idx = (curr_idx - 1) % total_songs
                st.session_state.current_track_index = prev_idx
                next_track = st.session_state.playlist[prev_idx]
                st.session_state.current_preview_url = next_track.get('preview_url')
                st.session_state.current_track_name = next_track.get('name')
                st.rerun()
        with ctrl_c2:
            st.markdown("<div style='text-align:center; font-size:11px; color:#888; line-height:35px;'>AI DJ</div>", unsafe_allow_html=True)
        with ctrl_c3:
            if st.button("ถัดไป ⏭️️", key="next_track", use_container_width=True):
                next_idx = (curr_idx + 1) % total_songs
                st.session_state.current_track_index = next_idx
                next_track = st.session_state.playlist[next_idx]
                st.session_state.current_preview_url = next_track.get('preview_url')
                st.session_state.current_track_name = next_track.get('name')
                st.rerun()

    # JavaScript เพิ่มฟังก์ชันลากย้ายตำแหน่ง
    st.markdown("""
    <script>
    setTimeout(function() {
        var player = document.querySelector('div[data-testid="stVerticalBlock"] > div:has(div.floating-marker)');
        var handle = document.getElementById('drag-handle');
        if (player && handle) {
            var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            handle.onmousedown = function(e) {
                e = e || window.event;
                e.preventDefault();
                pos3 = e.clientX;
                pos4 = e.clientY;
                document.onmouseup = function() {
                    document.onmouseup = null;
                    document.onmousemove = null;
                };
                document.onmousemove = function(e) {
                    e = e || window.event;
                    e.preventDefault();
                    pos1 = pos3 - e.clientX;
                    pos2 = pos4 - e.clientY;
                    pos3 = e.clientX;
                    pos4 = e.clientY;
                    player.style.top = (player.offsetTop - pos2) + "px";
                    player.style.left = (player.offsetLeft - pos1) + "px";
                    player.style.bottom = 'auto';
                    player.style.right = 'auto';
                };
            };
        }
    }, 300);
    </script>
    """, unsafe_allow_html=True)
