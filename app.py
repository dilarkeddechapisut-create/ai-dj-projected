import streamlit as st
import time

# นำเข้า Service ต่างๆ ของคุณ
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
    /* พื้นหลัง Gradient อนิเมชั่น */
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

    /* Flip Card CSS */
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

    /* =========================================
       Floating Player (CSS รองรับคอมฯ และ มือถือ)
       ========================================= */
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
        transition: all 0.3s ease;
    }
    
    /* การปรับขนาดอัตโนมัติเมื่ออยู่บนหน้าจอมือถือ */
    @media (max-width: 768px) {
        .floating-player {
            bottom: 15px;
            right: 15px;
            left: 15px; /* ตรึงขอบซ้ายขวา */
            width: calc(100vw - 30px); /* ยืดเต็มความกว้างมือถือ */
            padding: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. State Management สำหรับเครื่องเล่นเพลง
# ==========================================
if 'current_preview_url' not in st.session_state:
    st.session_state.current_preview_url = None
if 'current_track_name' not in st.session_state:
    st.session_state.current_track_name = ""
if 'play_timestamp' not in st.session_state:
    st.session_state.play_timestamp = 0 # ใช้บังคับให้บราวเซอร์เริ่มเล่นเพลงใหม่

st.title("🎧 AI DJ: จัดเพลย์ลิสต์ตามความรู้สึก")
st.markdown("บอกความรู้สึกของคุณมาให้เราฟัง แล้ว AI จะจัดเพลงที่ใช่ให้คุณเอง!")

# ==========================================
# 3. ส่วน Input
# ==========================================
col1, col2 = st.columns([2, 1])
with col1:
    mood_text = st.text_input("💬 พิมพ์ความรู้สึกของคุณที่นี่:", placeholder="เช่น วันนี้เหนื่อยจังเลย อยากได้เพลงปลอบใจ...")
    st.markdown("**หรือใช้ไมโครโฟนพูดความรู้สึก:**")
    audio_input = st.audio_input("พูดความรู้สึก") 
with col2:
    num_songs = st.slider("🎵 จำนวนเพลงที่ต้องการ", min_value=1, max_value=10, value=5)

# ประมวลผลเมื่อกดปุ่ม
if st.button("✨ ให้ AI จัดเพลย์ลิสต์", type="primary", use_container_width=True):
    if audio_input:
        st.info("กำลังประมวลผลเสียง... (ในเวอร์ชั่นนี้จะใช้ข้อความที่พิมพ์เป็นหลักก่อน)")
    
    if mood_text:
        with st.spinner("AI กำลังวิเคราะห์ความรู้สึกและค้นหาเพลง..."):
            ai_result = get_playlist_from_ai(mood_text, num_songs)
            
            if ai_result:
                st.success("🎉 จัดเพลย์ลิสต์เสร็จเรียบร้อย!")
                st.markdown(f"### 💌 ข้อความจาก AI DJ:\n> *{ai_result['encouragement']}*")
                st.divider()
                
                valid_tracks = []
                cols = st.columns(3)
                
                for i, song in enumerate(ai_result['songs']):
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
                        valid_tracks.append(track_info)
                        col_idx = i % 3
                        with cols[col_idx]:
                            # Card HTML
                            st.markdown(f"""
                            <div class="flip-card">
                              <div class="flip-card-inner">
                                <div class="flip-card-front">
                                  <img src="{track_info['album_cover']}" alt="Album Cover">
                                </div>
                                <div class="flip-card-back">
                                  <h4>{track_info['name']}</h4>
                                  <p>{track_info['artist']}</p>
                                  <hr/>
                                  <p style="font-size: 0.9em; font-style: italic;">{song['reason']}</p>
                                </div>
                              </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # ปุ่มกดฟังเพลง (เมื่อกดจะดึงข้อมูลเข้า session_state แล้วสุ่ม timestamp ใหม่)
                            if track_info.get('preview_url'):
                                if st.button(f"▶️ ฟังตัวอย่าง", key=f"play_{i}", use_container_width=True):
                                    st.session_state.current_preview_url = track_info['preview_url']
                                    st.session_state.current_track_name = track_info['name']
                                    st.session_state.play_timestamp = time.time() # อัปเดตเพื่อให้ Streamlit รู้ว่าเป็นเพลงใหม่
                                    st.rerun() 
                            else:
                                st.button("❌ ไม่มีตัวอย่างเพลง", key=f"play_{i}", disabled=True, use_container_width=True)
                            
                            st.markdown(f"<div style='text-align:center;'>[เปิดฟังเวอร์ชันเต็ม]({track_info.get('spotify_url', '#')})</div>", unsafe_allow_html=True)
                
                # แสดงกราฟวิเคราะห์ (Stats)
                st.divider()
                st.subheader("📈 วิเคราะห์สถิติของ Playlist")
                try:
                    fig = create_radar_chart(valid_tracks)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.info("ไม่สามารถสร้างกราฟสถิติได้เนื่องจากข้อมูลไม่ครบถ้วน")

                # ระบบ Feedback
                st.divider()
                st.subheader("📝 คุณชอบเพลย์ลิสต์นี้ไหม?")
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    if st.button("👍 ชอบมาก", use_container_width=True):
                        save_feedback(mood_text, True)
                        st.success("บันทึกความเห็นเรียบร้อย ขอบคุณครับ!")
                with f_col2:
                    if st.button("👎 ยังไม่โดนใจ", use_container_width=True):
                        save_feedback(mood_text, False)
                        st.info("เราจะนำไปปรับปรุงให้ดีขึ้นครับ!")
    else:
        st.warning("⚠️ กรุณาพิมพ์ความรู้สึกของคุณก่อนครับ")

# ==========================================
# 4. Floating Player UI (อัปเดตใหม่)
# ==========================================
if st.session_state.current_preview_url:
    # ฝัง Timestamp เข้าไปใน ID เครื่องเล่น เพื่อบังคับให้โหลด Component ใหม่ทุกครั้งที่กดปุ่ม
    player_id = f"audio-player-{st.session_state.play_timestamp}"
    
    floating_player_html = f"""
    <div class="floating-player" id="floating-music-box">
        <!-- ส่วนหัว (ชื่อเพลง + ปุ่มปิด) -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="color: #1DB954; font-weight: bold; font-size: 14px; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding-right: 10px;">
                🎵 กำลังเล่น: {st.session_state.current_track_name}
            </div>
            <button onclick="document.getElementById('floating-music-box').style.display='none'" 
                    style="background: transparent; border: none; color: #fff; font-size: 20px; cursor: pointer; padding: 0; line-height: 1;">
                &times;
            </button>
        </div>
        
        <!-- แท็กเครื่องเล่นเสียง -->
        <audio id="{player_id}" controls autoplay style="width: 100%; height: 45px; border-radius: 8px; outline: none;">
            <source src="{st.session_state.current_preview_url}" type="audio/mpeg">
            เบราว์เซอร์ของคุณไม่รองรับเครื่องเล่นเสียง
        </audio>
    </div>
    """
    st.markdown(floating_player_html, unsafe_allow_html=True)
