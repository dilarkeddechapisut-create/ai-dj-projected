import streamlit as st
from ai_service import get_playlist_from_ai
from spotify_service import search_spotify_track
from stats_service import create_radar_chart
from feedback_service import save_feedback
import time

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(page_title="AI DJ Mood Matcher", page_icon="🎧", layout="wide")

# 2. CSS สำหรับพื้นหลัง, อนิเมชั่น, Flip Cards และ Floating Player
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

    /* Floating Player (มุมขวาล่าง) */
    .floating-player {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #1DB954;
        padding: 15px;
        border-radius: 20px;
        z-index: 9999;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
        text-align: center;
        width: 300px;
    }
</style>
""", unsafe_allow_html=True)

# 3. State Management สำหรับเครื่องเล่นเพลง
if 'current_preview_url' not in st.session_state:
    st.session_state.current_preview_url = None
if 'current_track_name' not in st.session_state:
    st.session_state.current_track_name = ""

st.title("🎧 AI DJ: จัดเพลย์ลิสต์ตามความรู้สึก")
st.markdown("บอกความรู้สึกของคุณมาให้เราฟัง แล้ว AI จะจัดเพลงที่ใช่ให้คุณเอง!")

# 4. ส่วน Input (Text, Mic, Slider)
col1, col2 = st.columns([2, 1])
with col1:
    mood_text = st.text_input("💬 พิมพ์ความรู้สึกของคุณที่นี่:", placeholder="เช่น วันนี้เหนื่อยจังเลย อยากได้เพลงปลอบใจ...")
    st.markdown("**หรือใช้ไมโครโฟนพูดความรู้สึก:**")
    audio_input = st.audio_input("พูดความรู้สึก") # Widget อัดเสียงใหม่ล่าสุดของ Streamlit
with col2:
    num_songs = st.slider("🎵 จำนวนเพลงที่ต้องการ", min_value=1, max_value=10, value=5)

# ประมวลผลเมื่อกดปุ่ม
if st.button("✨ ให้ AI จัดเพลย์ลิสต์", type="primary", use_container_width=True):
    # ถ้ามีเสียง ให้อัพเดท mood_text (ในโปรเจกต์จริงสามารถส่ง audio ให้ Gemini โดยตรงได้)
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
                
                # นำชื่อเพลงจาก AI ไปหาใน Spotify
                cols = st.columns(3) # แสดงทีละ 3 คอลัมน์
                for i, song in enumerate(ai_result['songs']):
                    track_info = search_spotify_track(song['title'], song['artist'])
                    
                    if track_info:
                        valid_tracks.append(track_info)
                        col_idx = i % 3
                        with cols[col_idx]:
                            # สร้าง Flip Card HTML
                            st.markdown(f"""
                            <div class="flip-card">
                              <div class="flip-card-inner">
                                <div class="flip-card-front">
                                  <img src="{track_info['album_cover']}" alt="Avatar">
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
                            
                            # ปุ่มกดฟังตัวอย่าง (อัปเดต Floating Player)
                            if track_info['preview_url']:
                                if st.button(f"▶️ ฟังตัวอย่าง", key=f"play_{i}"):
                                    st.session_state.current_preview_url = track_info['preview_url']
                                    st.session_state.current_track_name = track_info['name']
                                    st.rerun() # สั่งรีรันหน้าเว็บเพื่ออัปเดตเครื่องเล่น
                            else:
                                st.button("❌ ไม่มีตัวอย่างเพลง", key=f"play_{i}", disabled=True)
                            
                            st.markdown(f"[เปิดใน Spotify]({track_info['spotify_url']})")
                
                # แสดงกราฟวิเคราะห์ (Stats)
                st.divider()
                st.subheader("📈 วิเคราะห์สถิติของ Playlist")
                fig = create_radar_chart(valid_tracks)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

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

# 5. Floating Player Rendering (เรนเดอร์เครื่องเล่นเมื่อมีการกดฟัง)
if st.session_state.current_preview_url:
    floating_player_html = f"""
    <div class="floating-player">
        <h4 style="margin-top:0; color: #1DB954;">กำลังเล่น 🎵</h4>
        <p style="font-weight: bold;">{st.session_state.current_track_name}</p>
        <audio controls autoplay style="width: 100%;">
            <source src="{st.session_state.current_preview_url}" type="audio/mpeg">
            เบราว์เซอร์ของคุณไม่รองรับเครื่องเล่นเสียง
        </audio>
    </div>
    """
    st.markdown(floating_player_html, unsafe_allow_html=True)
