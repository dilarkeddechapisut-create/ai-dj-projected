import streamlit as st
import time

# นำเข้า Service ต่างๆ (ใช้ของเดิมของคุณได้เลย)
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

    /* Floating Player */
    .floating-player {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(15, 32, 39, 0.95);
        border: 2px solid #1DB954;
        padding: 15px;
        border-radius: 16px;
        z-index: 999999;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        backdrop-filter: blur(10px);
        width: 320px;
    }
    @media (max-width: 768px) {
        .floating-player {
            bottom: 15px;
            right: 15px;
            left: 15px;
            width: calc(100vw - 30px);
            padding: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. State Management (ป้องกันเพลงหายตอนรีเฟรช)
# ==========================================
if 'playlist' not in st.session_state:
    st.session_state.playlist = [] 
if 'ai_message' not in st.session_state:
    st.session_state.ai_message = "" 
if 'current_preview_url' not in st.session_state:
    st.session_state.current_preview_url = None 
if 'current_track_name' not in st.session_state:
    st.session_state.current_track_name = "" 
if 'play_timestamp' not in st.session_state:
    st.session_state.play_timestamp = 0

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

# เมื่อกดปุ่ม ให้ดึงข้อมูลมาเก็บไว้ใน session_state อย่างเดียว
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
                
                # บันทึกข้อมูลลง session_state
                st.session_state.playlist = valid_tracks
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
            
            if track_info.get('preview_url'):
                if st.button(f"▶️ ฟังตัวอย่าง", key=f"play_{i}", use_container_width=True):
                    st.session_state.current_preview_url = track_info['preview_url']
                    st.session_state.current_track_name = track_info['name']
                    st.session_state.play_timestamp = time.time() 
                    st.rerun() 
            else:
                st.button("❌ ไม่มีตัวอย่าง", key=f"no_play_{i}", disabled=True, use_container_width=True)
            
            st.markdown(f"<div style='text-align:center;'>[เปิดฟังเต็มบน Spotify]({track_info.get('spotify_url', '#')})</div><br>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📈 วิเคราะห์สถิติของ Playlist")
    try:
        fig = create_radar_chart(st.session_state.playlist)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("ไม่สามารถสร้างกราฟสถิติได้")

# ==========================================
# 5. Floating Player
# ==========================================
if st.session_state.current_preview_url:
    player_id = f"audio-player-{st.session_state.play_timestamp}"
    
    floating_player_html = f"""
    <div class="floating-player" id="floating-music-box">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="color: #1DB954; font-weight: bold; font-size: 14px; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding-right: 10px;">
                🎵 กำลังเล่น: {st.session_state.current_track_name}
            </div>
            <button onclick="document.getElementById('floating-music-box').style.display='none'" 
                    style="background: transparent; border: none; color: #fff; font-size: 20px; cursor: pointer; padding: 0; line-height: 1;">
                &times;
            </button>
        </div>
        
        <!-- เอา type="audio/mpeg" ออก เพื่อให้บราวเซอร์ตรวจจับไฟล์ .m4a หรือ .mp3 เองอัตโนมัติ -->
        <audio id="{player_id}" controls autoplay style="width: 100%; height: 45px; border-radius: 8px; outline: none;">
            <source src="{st.session_state.current_preview_url}">
        </audio>
    </div>
    """
    st.markdown(floating_player_html, unsafe_allow_html=True)
