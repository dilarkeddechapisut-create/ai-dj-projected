import json
import time
from datetime import datetime
import urllib.parse
import re
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text

# นำเข้า Service ต่างๆ
from ai_service import get_playlist_from_ai
from spotify_service import search_spotify_track
from stats_service import create_radar_chart
from feedback_service import save_feedback, save_mood_history, get_user_saved_data
from preview_service import get_track_preview, DEFAULT_COVER, FALLBACK_AUDIO_URL
from auth_service import (
    sign_in_with_email_and_password, 
    sign_up_with_email_and_password, 
    reset_password
)

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="DJ Moody",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BG_IMAGE_URL = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2000&auto=format&fit=crop"
BG_VIDEO_URL = "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_083109_283f3553-e28f-428b-a723-d639c617eb2b.mp4"

# ==========================================
# 2. Liquid Glass Music Player Renderer
# ==========================================
def render_liquid_music_player(playlist=None, start_index=0, autoplay=True):
    if not playlist:
        return

    playlist_json = json.dumps(playlist)

    player_code = f"""
    <script>
    (function() {{
        const parentDoc = window.parent.document;
        
        const oldPlayer = parentDoc.getElementById('liquid-glass-player');
        if (oldPlayer) {{
            oldPlayer.remove();
        }}

        const playlist = {playlist_json};
        let currentTrack = {start_index};
        let isPlaying = {'true' if autoplay else 'false'};

        const player = parentDoc.createElement('div');
        player.id = 'liquid-glass-player';
        player.innerHTML = `
            <style>
                #liquid-glass-player {{
                    position: fixed;
                    bottom: 25px;
                    right: 25px;
                    width: 330px;
                    padding: 16px 18px;
                    border-radius: 22px;
                    background: rgba(18, 22, 34, 0.85);
                    backdrop-filter: blur(20px) saturate(180%);
                    -webkit-backdrop-filter: blur(20px) saturate(180%);
                    border: 1px solid rgba(255, 255, 255, 0.22);
                    box-shadow: 0 12px 35px 0 rgba(0, 0, 0, 0.5),
                                inset 0 1px 1px 0 rgba(255, 255, 255, 0.3);
                    z-index: 999999;
                    font-family: -apple-system, BlinkMacSystemFont, "Prompt", "Segoe UI", Roboto, sans-serif;
                    color: #ffffff;
                    user-select: none;
                    transition: box-shadow 0.3s ease;
                }}

                #liquid-glass-player:hover {{
                    box-shadow: 0 16px 45px 0 rgba(0, 0, 0, 0.7),
                                inset 0 1px 2px 0 rgba(255, 255, 255, 0.4);
                }}

                .lg-drag-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    cursor: grab;
                    padding-bottom: 8px;
                    margin-bottom: 10px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
                }}

                .lg-drag-header:active {{
                    cursor: grabbing;
                }}

                .lg-brand {{
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    color: #1DB954;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }}

                .lg-close-btn {{
                    background: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 0.6);
                    cursor: pointer;
                    font-size: 13px;
                    line-height: 1;
                    padding: 2px 6px;
                    border-radius: 50%;
                    transition: all 0.2s;
                }}

                .lg-close-btn:hover {{
                    color: #ffffff;
                    background: rgba(255, 255, 255, 0.2);
                }}

                .lg-body {{
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}

                .lg-cover {{
                    width: 50px;
                    height: 50px;
                    border-radius: 14px;
                    object-fit: cover;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    flex-shrink: 0;
                }}

                .lg-info {{
                    flex: 1;
                    min-width: 0;
                }}

                .lg-title {{
                    font-size: 13px;
                    font-weight: 600;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    color: #ffffff;
                }}

                .lg-artist {{
                    font-size: 11px;
                    color: rgba(255, 255, 255, 0.75);
                    margin-top: 2px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }}

                .lg-progress-container {{
                    margin-top: 10px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}

                .lg-time {{
                    font-size: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-variant-numeric: tabular-nums;
                }}

                .lg-progress-bar {{
                    flex: 1;
                    height: 5px;
                    background: rgba(255, 255, 255, 0.22);
                    border-radius: 10px;
                    overflow: hidden;
                    cursor: pointer;
                    position: relative;
                }}

                .lg-progress-fill {{
                    height: 100%;
                    width: 0%;
                    background: linear-gradient(90deg, #1DB954, #1ed760);
                    border-radius: 10px;
                }}

                .lg-controls {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 14px;
                    margin-top: 10px;
                }}

                .lg-btn {{
                    background: rgba(255, 255, 255, 0.12);
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    color: white;
                    border-radius: 50%;
                    width: 34px;
                    height: 34px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }}

                .lg-btn:hover {{
                    background: rgba(255, 255, 255, 0.3);
                    transform: scale(1.08);
                }}

                .lg-btn-play {{
                    width: 40px;
                    height: 40px;
                    background: #1DB954;
                    border: 1px solid rgba(255, 255, 255, 0.4);
                    box-shadow: 0 4px 15px rgba(29, 185, 84, 0.5);
                }}

                .lg-btn-play:hover {{
                    background: #1ed760;
                }}
            </style>

            <div class="lg-drag-header" id="lg-drag-handle">
                <span class="lg-brand">
                    <svg width="12" height="12" fill="currentColor" viewBox="0 0 24 24">
                        <circle cx="5" cy="5" r="2"/><circle cx="12" cy="5" r="2"/><circle cx="19" cy="5" r="2"/>
                        <circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/>
                    </svg>
                    DJ MOODY PLAYER
                </span>
                <button class="lg-close-btn" id="lg-close-btn" title="ปิดตัวเล่นเพลง">✖</button>
            </div>

            <div class="lg-body">
                <img id="lg-cover-img" class="lg-cover" src="" alt="cover" />
                <div class="lg-info">
                    <div id="lg-title-text" class="lg-title"></div>
                    <div id="lg-artist-text" class="lg-artist"></div>
                </div>
            </div>

            <div class="lg-progress-container">
                <span class="lg-time" id="lg-current-time">0:00</span>
                <div class="lg-progress-bar" id="lg-progress-bar">
                    <div class="lg-progress-fill" id="lg-progress-fill"></div>
                </div>
                <span class="lg-time" id="lg-duration">0:00</span>
            </div>

            <div class="lg-controls">
                <button class="lg-btn" id="lg-prev-btn">
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
                </button>
                <button class="lg-btn lg-btn-play" id="lg-play-btn">
                    <svg id="lg-play-icon" width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                </button>
                <button class="lg-btn" id="lg-next-btn">
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
                </button>
            </div>

            <audio id="lg-audio-element"></audio>
        `;

        parentDoc.body.appendChild(player);

        const audio = parentDoc.getElementById('lg-audio-element');
        const playBtn = parentDoc.getElementById('lg-play-btn');
        const playIcon = parentDoc.getElementById('lg-play-icon');
        const prevBtn = parentDoc.getElementById('lg-prev-btn');
        const nextBtn = parentDoc.getElementById('lg-next-btn');
        const closeBtn = parentDoc.getElementById('lg-close-btn');
        const titleText = parentDoc.getElementById('lg-title-text');
        const artistText = parentDoc.getElementById('lg-artist-text');
        const coverImg = parentDoc.getElementById('lg-cover-img');
        const progressFill = parentDoc.getElementById('lg-progress-fill');
        const progressBar = parentDoc.getElementById('lg-progress-bar');
        const currentTimeEl = parentDoc.getElementById('lg-current-time');
        const durationEl = parentDoc.getElementById('lg-duration');
        const dragHandle = parentDoc.getElementById('lg-drag-handle');

        function loadTrack(index) {{
            currentTrack = index;
            const track = playlist[currentTrack];
            if (!track) return;
            titleText.innerText = track.title || 'Unknown Title';
            artistText.innerText = track.artist || 'Unknown Artist';
            coverImg.src = track.cover || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300';
            audio.src = track.url;
            progressFill.style.width = '0%';
            currentTimeEl.innerText = '0:00';
            durationEl.innerText = '0:00';

            if (isPlaying) {{
                audio.play().then(() => {{
                    playIcon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
                }}).catch(() => {{
                    isPlaying = false;
                    playIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
                }});
            }} else {{
                playIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
            }}
        }}

        function togglePlay() {{
            if (audio.paused) {{
                audio.play().then(() => {{
                    isPlaying = true;
                    playIcon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
                }}).catch(e => console.log(e));
            }} else {{
                audio.pause();
                isPlaying = false;
                playIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
            }}
        }}

        playBtn.addEventListener('click', togglePlay);

        prevBtn.addEventListener('click', () => {{
            let index = currentTrack - 1;
            if (index < 0) index = playlist.length - 1;
            isPlaying = true;
            loadTrack(index);
        }});

        nextBtn.addEventListener('click', () => {{
            let index = (currentTrack + 1) % playlist.length;
            isPlaying = true;
            loadTrack(index);
        }});

        closeBtn.addEventListener('click', () => {{
            audio.pause();
            player.remove();
        }});

        audio.addEventListener('timeupdate', () => {{
            if (audio.duration) {{
                const pct = (audio.currentTime / audio.duration) * 100;
                progressFill.style.width = pct + '%';
                currentTimeEl.innerText = formatTime(audio.currentTime);
                durationEl.innerText = formatTime(audio.duration);
            }}
        }});

        audio.addEventListener('ended', () => {{
            let index = (currentTrack + 1) % playlist.length;
            isPlaying = true;
            loadTrack(index);
        }});

        progressBar.addEventListener('click', (e) => {{
            const rect = progressBar.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            if (audio.duration) {{
                audio.currentTime = (clickX / rect.width) * audio.duration;
            }}
        }});

        function formatTime(sec) {{
            const m = Math.floor(sec / 60);
            const s = Math.floor(sec % 60);
            return `${{m}}:${{s < 10 ? '0' : ''}}${{s}}`;
        }}

        let isDragging = false;
        let startX, startY, initialLeft, initialTop;

        function onMouseDown(e) {{
            if (e.target === closeBtn) return;
            isDragging = true;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            
            const rect = player.getBoundingClientRect();
            startX = clientX;
            startY = clientY;
            initialLeft = rect.left;
            initialTop = rect.top;

            player.style.bottom = 'auto';
            player.style.right = 'auto';
            player.style.left = initialLeft + 'px';
            player.style.top = initialTop + 'px';

            parentDoc.addEventListener('mousemove', onMouseMove);
            parentDoc.addEventListener('mouseup', onMouseUp);
            parentDoc.addEventListener('touchmove', onMouseMove);
            parentDoc.addEventListener('touchend', onMouseUp);
        }}

        function onMouseMove(e) {{
            if (!isDragging) return;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;

            const deltaX = clientX - startX;
            const deltaY = clientY - startY;

            let newLeft = initialLeft + deltaX;
            let newTop = initialTop + deltaY;

            newLeft = Math.max(10, Math.min(window.innerWidth - player.offsetWidth - 10, newLeft));
            newTop = Math.max(10, Math.min(window.innerHeight - player.offsetHeight - 10, newTop));

            player.style.left = newLeft + 'px';
            player.style.top = newTop + 'px';
        }}

        function onMouseUp() {{
            isDragging = false;
            parentDoc.removeEventListener('mousemove', onMouseMove);
            parentDoc.removeEventListener('mouseup', onMouseUp);
            parentDoc.removeEventListener('touchmove', onMouseMove);
            parentDoc.removeEventListener('touchend', onMouseUp);
        }}

        dragHandle.addEventListener('mousedown', onMouseDown);
        dragHandle.addEventListener('touchstart', onMouseDown);

        loadTrack(currentTrack);
    }})();
    </script>
    """
    components.html(player_code, height=0, width=0)

# ==========================================
# 3. Responsive Custom CSS
# ==========================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        background: url('{BG_IMAGE_URL}') no-repeat center center fixed !important;
        background-size: cover !important;
        font-family: 'Prompt', sans-serif !important;
        color: #ffffff !important;
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(10, 15, 20, 0.45);
        z-index: -9998;
        pointer-events: none;
    }}

    .stApp {{
        background: transparent !important;
        color: #ffffff !important;
    }}

    #bg-video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -9997;
        object-fit: cover;
        filter: brightness(0.4);
        pointer-events: none;
    }}

    h1, h2, h3, h4, h5, h6, p, span, div {{
        color: #ffffff !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9);
    }}

    div[data-testid="stMetric"] {{
        background: rgba(18, 18, 24, 0.82) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.6) !important;
    }}

    div[data-testid="stMetricLabel"] p {{
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stMetricValue"] div {{
        color: #1DB954 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 12px rgba(29, 185, 84, 0.6) !important;
    }}

    /* ปรับแต่ง Label หัวข้อช่องกรอกข้อมูลให้คมชัด */
    label, 
    .stWidgetLabel, 
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p,
    label p, 
    label span {{
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.95) !important;
    }}

    /* ปรับแต่ง Textarea & Input Box ให้เป็นสีเข้ม Glassmorphic อ่านง่าย ตัวหนังสือขาวคมชัด */
    .stTextArea textarea,
    .stTextInput input,
    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {{
        background-color: rgba(18, 22, 32, 0.92) !important;
        background: rgba(18, 22, 32, 0.92) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        font-family: 'Prompt', sans-serif !important;
        border-radius: 14px !important;
    }}

    div[data-baseweb="input"],
    div[data-baseweb="textarea"] {{
        border: 1.5px solid rgba(255, 255, 255, 0.35) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6) !important;
    }}

    /* เมื่อคลิกพิมพ์ที่กล่องข้อความ (Focus State) */
    .stTextArea textarea:focus,
    .stTextInput input:focus,
    div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="input"]:focus-within {{
        border-color: #1DB954 !important;
        box-shadow: 0 0 15px rgba(29, 185, 84, 0.6) !important;
    }}

    /* ข้อความ Placeholder ในช่องกรอก */
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder,
    div[data-baseweb="input"] input::placeholder {{
        color: rgba(255, 255, 255, 0.55) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.55) !important;
    }}

    div[data-baseweb="select"] > div {{
        background: rgba(18, 18, 22, 0.92) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }}

    div[data-baseweb="select"] * {{
        color: #ffffff !important;
    }}

    div[role="listbox"] {{
        background-color: #1e1e24 !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }}

    div[role="option"] {{
        color: #ffffff !important;
    }}

    div[data-testid="stSlider"] * {{
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9) !important;
    }}

    iframe,
    iframe[title="streamlit_mic_recorder.speech_to_text"],
    div[data-testid="stCustomComponentV1"],
    div[data-testid="stElementContainer"]:has(iframe) {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* สไตล์ปุ่มกดทั่วไป และ Streaming Link Button */
    div.stButton > button,
    div.stLinkButton > a {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.25s ease-in-out !important;
        width: 100% !important;
        text-align: center !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.4rem 0.8rem !important;
    }}

    div.stButton > button:hover,
    div.stLinkButton > a:hover {{
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
        box-shadow: 0 10px 35px 0 rgba(29, 185, 84, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px);
        color: #ffffff !important;
    }}

    div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, rgba(29, 185, 84, 0.9), rgba(20, 140, 60, 0.95)) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 25px rgba(29, 185, 84, 0.45) !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 10px !important;
        background: rgba(18, 18, 22, 0.8);
        backdrop-filter: blur(16px);
        padding: 8px 16px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        width: fit-content;
        margin: 0 auto;
    }}

    div[data-testid="stRadio"] label {{
        background: rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        padding: 8px 18px !important;
        font-weight: 500 !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
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
        background: rgba(18, 18, 24, 0.82);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
        font-size: 0.98rem;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .spotify-card-subtitle {{
        font-size: 0.85rem;
        color: #cccccc;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .spotify-tag {{
        display: inline-block;
        background: rgba(29, 185, 84, 0.35);
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
        text-shadow: 0 4px 15px rgba(0, 0, 0, 0.9);
    }}

    .user-badge {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 6px 16px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.28);
        font-size: 0.88rem;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #ffffff;
    }}

    div[data-testid="stExpander"] {{
        background: rgba(18, 18, 22, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 12px !important;
    }}
    div[data-testid="stExpander"] details summary span {{
        color: #ffffff !important;
    }}
</style>

<video autoplay loop muted playsinline id="bg-video">
    <source src="{BG_VIDEO_URL}" type="video/mp4">
</video>
""", unsafe_allow_html=True)

# ==========================================
# 4. State Management
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
if 'ai_taste_analysis' not in st.session_state:
    st.session_state.ai_taste_analysis = ""
if 'ai_taste_recommendations' not in st.session_state:
    st.session_state.ai_taste_recommendations = []

# ==========================================
# 5. Helper Functions
# ==========================================
def format_ai_analysis_to_html(text):
    """จัดรูปแบบ Markdown ข้อความของ AI ให้แสดงผลสวยงามและ fit ใน Glass Card"""
    if not text:
        return ""
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #1ed760; font-weight: 600;">\1</strong>', text)
    lines = formatted.split('\n')
    html_lines = []
    for line in lines:
        l = line.strip()
        if not l:
            continue
        if l.startswith('- ') or l.startswith('* '):
            html_lines.append(f'<li style="margin-left: 20px; margin-bottom: 6px; color: #e0e0e0; line-height: 1.6;">{l[2:]}</li>')
        elif any(l.startswith(f"{i}.") for i in range(1, 10)):
            html_lines.append(f'<div style="font-size: 1.05rem; margin-top: 16px; margin-bottom: 8px; font-weight: 600; color: #ffffff;">{l}</div>')
        else:
            html_lines.append(f'<p style="margin-bottom: 12px; line-height: 1.7; color: rgba(255, 255, 255, 0.92);">{l}</p>')
    return "".join(html_lines)

@st.cache_data(ttl=3600)
def fetch_live_track_info(title, artist, tag):
    try:
        track_info = search_spotify_track(title, artist)
    except Exception:
        track_info = None

    try:
        img_url, preview_url, full_url = get_track_preview(title, artist)
    except Exception:
        img_url, preview_url, full_url = DEFAULT_COVER, FALLBACK_AUDIO_URL, None

    spotify_cover = track_info.get('album_cover') if track_info else None
    cover = spotify_cover if spotify_cover else (img_url if img_url else DEFAULT_COVER)
    
    spotify_preview = track_info.get('preview_url') if track_info else None
    preview = spotify_preview if spotify_preview else (preview_url if preview_url else FALLBACK_AUDIO_URL)

    encoded_search = urllib.parse.quote(f"{title} {artist}")
    spotify_link = (track_info.get('spotify_url') if track_info else None) or full_url or f"https://open.spotify.com/search/{encoded_search}"
    spotify_id = track_info.get('id') if track_info else None

    official_title = track_info.get('name') if track_info else title
    official_artist = track_info.get('artist') if track_info else artist

    return {
        "id": spotify_id,
        "name": official_title,
        "artist": official_artist,
        "tag": tag,
        "cover": cover,
        "preview": preview,
        "spotify_url": spotify_link
    }

def handle_like_song(track, mood_prompt=""):
    is_fav = any(f['name'] == track['name'] for f in st.session_state.favorites)
    user_email = st.session_state.user.get('email', 'Anonymous') if st.session_state.user else 'Anonymous'
    
    if is_fav:
        st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != track['name']]
        save_feedback(
            user_email=user_email,
            mood_text=mood_prompt or st.session_state.user_input_text or "ยกเลิกถูกใจ",
            song_name=track['name'],
            artist=track.get('artist', ''),
            is_liked=False
        )
        st.toast(f"ลบ {track['name']} ออกจากรายการโปรดแล้ว", icon="🗑")
    else:
        st.session_state.favorites.append(track)
        try:
            current_mood = mood_prompt or st.session_state.user_input_text or "กดถูกใจจากรายการแนะนำ"
            save_feedback(
                user_email=user_email,
                mood_text=current_mood,
                song_name=track['name'],
                artist=track.get('artist', ''),
                is_liked=True
            )
            st.toast(f"เพิ่ม {track['name']} ในเพลงโปรดเรียบร้อย! 💖", icon="✅")
        except Exception:
            st.toast(f"เพิ่ม {track['name']} ในเพลงโปรดแล้ว", icon="❤️")

# ==========================================
# 6. Firebase Authentication View
# ==========================================
if st.session_state.user is None:
    st.markdown("""
    <div class="main-header">
        <h1>🎧 DJ Moody</h1>
        <p style="color: #ddd;">กรุณาเข้าสู่ระบบก่อนเริ่มใช้งานเพื่อบันทึกประวัติส่วนตัว</p>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
    
    with auth_col2:
        auth_mode = st.tabs(["🔐 เข้าสู่ระบบ", "📝 สมัครสมาชิก", "🔑 ลืมรหัสผ่าน"])
        
        with auth_mode[0]:
            st.subheader("เข้าสู่ระบบ")
            login_email = st.text_input("อีเมล", key="login_email_input", placeholder="your_email@gmail.com")
            login_pass = st.text_input("รหัสผ่าน", type="password", key="login_pass_input")
            
            if st.button("🚀 เข้าสู่ระบบ", type="primary", use_container_width=True, key="login_btn"):
                if login_email and login_pass:
                    with st.spinner("กำลังตรวจสอบข้อมูลและดึงประวัติส่วนตัว..."):
                        res = sign_in_with_email_and_password(login_email, login_pass)
                        if res["success"]:
                            st.session_state.user = res["info"]
                            user_data = get_user_saved_data(login_email)
                            st.session_state.history = user_data.get("history", [])
                            st.session_state.favorites = user_data.get("favorites", [])
                            st.success("เข้าสู่ระบบสำเร็จ!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(res["error"])
                else:
                    st.warning("กรุณากรอกอีเมลและรหัสผ่านให้ครบถ้วน")

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
                                st.session_state.history = []
                                st.session_state.favorites = []
                                st.success("สมัครสมาชิกสำเร็จและเข้าสู่ระบบเรียบร้อย!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(res["error"])
                else:
                    st.warning("กรุณากรอกข้อมูลให้ครบทุกช่อง")

        with auth_mode[2]:
            st.subheader("รีเซ็ตรหัสผ่าน")
            reset_email_input = st.text_input("กรอกอีเมลของคุณ", key="reset_email_input")
            
            if st.button("📧 ส่งลิงก์รีเซ็ตรหัสผ่าน", use_container_width=True, key="reset_btn"):
                if reset_email_input:
                    with st.spinner("กำลังส่งอีเมล..."):
                        res = reset_password(reset_email_input)
                        if res["success"]:
                            st.success("ส่งลิงก์รีเซ็ตรหัสผ่านไปยังอีเมลของคุณเรียบร้อยแล้ว")
                        else:
                            st.error(res["error"])
                else:
                    st.warning("กรุณากรอกอีเมล")

    st.stop()

# ==========================================
# 7. Main App Content
# ==========================================

top_c1, top_c2 = st.columns([3, 1])
with top_c1:
    st.markdown("""
    <div class="main-header" style="text-align: left; margin-bottom: 0;">
        <h1 style="font-size: 1.8rem; margin:0;">🎧 DJ Moody</h1>
    </div>
    """, unsafe_allow_html=True)

with top_c2:
    user_email = st.session_state.user.get('email', 'User')
    st.markdown(f"<div class='user-badge'>👤 {user_email}</div>", unsafe_allow_html=True)
    if st.button("🚪 ออกจากระบบ", key="logout_btn"):
        st.session_state.user = None
        st.session_state.playlist = []
        st.session_state.favorites = []
        st.session_state.history = []
        st.session_state.current_preview_url = None
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
        height=95
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
                current_user_email = st.session_state.user.get('email', 'Anonymous') if st.session_state.user else 'Anonymous'
                
                save_mood_history(
                    user_email=current_user_email,
                    mood_text=mood_text,
                    persona=dj_persona,
                    energy_level=energy_level
                )

                augmented_prompt = f"[สไตล์ DJ: {dj_persona}] [ระดับพลังงานเพลง: {energy_level}] [ข้อแนะนำ: ตอบข้อความทักทายให้กำลังใจแบบกระชับสั้นๆ ไม่เกิน 2 ประโยค] ความรู้สึกผู้ใช้: {mood_text}"
                ai_result = get_playlist_from_ai(augmented_prompt, num_songs)
                
                if ai_result:
                    st.session_state.ai_message = ai_result.get('encouragement', '')
                    valid_tracks = []
                    
                    for song in ai_result.get('songs', []):
                        track_data = fetch_live_track_info(song['title'], song['artist'], dj_persona)
                        track_info = {
                            'id': track_data.get('id'),
                            'name': track_data['name'],
                            'artist': track_data['artist'],
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
            st.warning("⚠ กรุณาพิมพ์หรือเลือกความรู้สึกของคุณก่อนครับ")

    if len(st.session_state.playlist) > 0:
        st.success("🎉 จัดเพลย์ลิสต์เสร็จเรียบร้อย!")
        
        st.markdown(f"""
        <div style="
            background: rgba(18, 22, 34, 0.88);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(29, 185, 84, 0.5);
            border-radius: 16px;
            padding: 16px 20px;
            margin: 15px 0 20px 0;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
        ">
            <div style="font-size: 1.15rem; font-weight: 700; color: #1DB954 !important; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                💌 ข้อความจาก {dj_persona}
            </div>
            <div style="font-size: 1.02rem; font-weight: 500; color: #ffffff !important; line-height: 1.6; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">
                "{st.session_state.ai_message}"
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, track_info in enumerate(st.session_state.playlist):
            reason_text = track_info.get('reason', 'เพลงนี้เหมาะกับบรรยากาศของคุณพอดี!')
            
            with cols[i % 3]:
                st.markdown(f"""
                <div class="spotify-card">
                    <div>
                        <div class="spotify-card-img-wrapper">
                            <img src="{track_info['album_cover']}" class="spotify-card-img" alt="Cover">
                        </div>
                        <div class="spotify-card-title">{track_info['name']}</div>
                        <div class="spotify-card-subtitle">{track_info['artist']}</div>
                        <div style="font-size:0.83rem; color:#e0e0e0; margin-top:10px; line-height:1.45; word-wrap: break-word;">
                            <strong style="color: #1DB954;">💡 คำแนะนำจาก DJ:</strong> {reason_text}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                btn_c1, btn_c2, btn_c3 = st.columns([1.2, 0.8, 1])
                with btn_c1:
                    if st.button("▶️ ฟังตัวอย่าง", key=f"play_dj_{i}", use_container_width=True):
                        st.session_state.current_preview_url = track_info['preview_url']
                        st.session_state.current_track_name = track_info['name']
                        st.session_state.current_track_index = i
                        st.rerun()
                
                with btn_c2:
                    is_fav = any(f['name'] == track_info['name'] for f in st.session_state.favorites)
                    if st.button("❤️" if is_fav else "🤍", key=f"fav_dj_{i}", use_container_width=True):
                        handle_like_song(track_info, mood_prompt=mood_text)
                        st.rerun()

                with btn_c3:
                    st.link_button("🎶 Streaming", track_info.get('spotify_url', '#'), use_container_width=True)

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
                <div>
                    <div class="spotify-card-img-wrapper">
                        <img src="{song['cover']}" class="spotify-card-img" alt="Album Art">
                    </div>
                    <span class="spotify-tag">{song['tag']}</span>
                    <div class="spotify-card-title">{song['name']}</div>
                    <div class="spotify-card-subtitle">{song['artist']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            p_col1, p_col2 = st.columns([1.5, 1])
            with p_col1:
                if st.button("▶️ ฟังตัวอย่าง", key=f"grid_play_{selected_mood}_{idx}", use_container_width=True):
                    st.session_state.current_preview_url = song['preview']
                    st.session_state.current_track_name = song['name']
                    st.rerun()
            
            with p_col2:
                is_fav = any(f['name'] == song['name'] for f in st.session_state.favorites)
                if st.button("❤" if is_fav else "🤍 เก็บไว้", key=f"grid_fav_{selected_mood}_{idx}", use_container_width=True):
                    track_dict = {
                        'id': song.get('id'),
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
# PAGE 3: 📊 สถิติ & วิเคราะห์
# ------------------------------------------
elif nav_choice == "📊 สถิติ & วิเคราะห์":
    st.subheader("📈 วิเคราะห์สถิติอารมณ์และรสนิยมดนตรี")
    
    analysis_source = st.radio(
        "🎯 เลือกชุดเพลงที่ต้องการวิเคราะห์:",
        ["❤️ เพลงในรายการโปรด", "✨ เพลงจาก AI DJ Studio"],
        horizontal=True,
        key="analysis_source_radio"
    )
    
    if analysis_source == "❤️ เพลงในรายการโปรด":
        target_playlist = st.session_state.favorites
        source_name = "รายการโปรด"
    else:
        target_playlist = st.session_state.playlist
        source_name = "AI DJ Studio"

    if len(target_playlist) > 0:
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("จำนวนเพลงทั้งหมด", f"{len(target_playlist)} เพลง")
        m_col2.metric("สถานะ FreqBlog API", "พร้อมใช้งาน 🟢")
        m_col3.metric("เพลงที่มีไฟล์ตัวอย่าง", f"{sum(1 for t in target_playlist if t.get('preview_url'))} เพลง")

        with st.spinner(f"กำลังดึงข้อมูล Audio Features ของ{source_name} จาก FreqBlog API..."):
            try:
                fig = create_radar_chart(target_playlist)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("ไม่สามารถวิเคราะห์ข้อมูลกราฟจาก FreqBlog ได้ในขณะนี้")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการสร้างกราฟ: {e}")

        st.divider()

        st.markdown(f"### 🤖 AI วิเคราะห์รสนิยมดนตรีจาก Audio Features ({source_name})")
        st.write("วิเคราะห์ลักษณะอารมณ์ทางดนตรี เช่น Energy, Danceability, Valence และ Acousticness เพื่อถอดรหัสตัวตนดนตรีของคุณ")

        if st.button(f"✨ ให้ AI ถอดรหัสรสนิยม & แนะนำเพลงจาก{source_name}", type="primary", use_container_width=True):
            with st.spinner("🧠 AI กำลังประมวลผล Audio Features และสร้างบทวิเคราะห์รสนิยมของคุณ..."):
                songs_summary = ", ".join([f"'{t.get('name')}' โดย {t.get('artist', 'ไม่ระบุ')}" for t in target_playlist])
                
                taste_prompt = f"""
                [บทบาท: ผู้เชี่ยวชาญด้าน Musicology และ AI Audio Feature Analyst]
                รบกวนวิเคราะห์รสนิยมการฟังเพลงของผู้ใช้ จากรายชื่อเพลงใน{source_name}ดังต่อไปนี้:
                {songs_summary}

                โปรดตอบและสรุปออกมาในหัวข้อดังนี้:
                1. 🎭 **โปรไฟล์รสนิยมดนตรี (Music Taste Profile):** วิเคราะห์สรุปภาพรวมลักษณะทางเสียง (Energy, Danceability, Valence/Emotional Mood, Acousticness, Tempo) ว่าผู้ใช้นี้ชอบฟังเพลงแนวไหน สไตล์อย่างไร และสะท้อนตัวตนหรืออารมณ์แบบไหน
                2. 🎧 **ช่วงเวลาและบรรยากาศที่เหมาะกับคุณ:** บอกกิจกรรม สถานการณ์ หรือช่วงเวลาที่เหมาะที่สุดกับการฟังเพลงสไตล์นี้
                3. 🌟 **แนะนำ 4 เพลงที่เหมาะกับรสนิยมของคุณเพิ่มเติม:** เลือกเพลงเพิ่มเติมที่มีค่า Audio Features และมู้ดใกล้เคียงกันพร้อมอธิบายเหตุผลสั้นๆ
                """

                ai_response = get_playlist_from_ai(taste_prompt, num_songs=4)
                if ai_response:
                    st.session_state.ai_taste_analysis = ai_response.get('encouragement', '')
                    st.session_state.ai_taste_recommendations = ai_response.get('songs', [])
                    st.toast("วิเคราะห์รสนิยมดนตรีเสร็จสิ้น!", icon="🎉")

        if st.session_state.ai_taste_analysis:
            content_html = format_ai_analysis_to_html(st.session_state.ai_taste_analysis)
            
            st.markdown(f"""
            <div style="
                background: rgba(18, 22, 34, 0.88); 
                backdrop-filter: blur(20px) saturate(180%);
                -webkit-backdrop-filter: blur(20px) saturate(180%);
                padding: 24px; 
                border-radius: 20px; 
                border: 1px solid rgba(29, 185, 84, 0.45); 
                margin-top: 20px; 
                margin-bottom: 25px;
                box-shadow: 0 12px 35px rgba(0,0,0,0.6);
            ">
                <h3 style="color: #1DB954 !important; margin-top:0; margin-bottom: 16px; font-size: 1.35rem; display: flex; align-items: center; gap: 8px;">
                    🔮 ผลการวิเคราะห์รสนิยมดนตรีของคุณ
                </h3>
                <div style="font-size: 0.98rem; color: #ffffff;">
                    {content_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.ai_taste_recommendations:
                st.markdown("#### 🎵 เพลงเพิ่มเติมที่ AI คัดสรรมาให้เหมาะกับรสนิยมของคุณ:")
                rec_cols = st.columns(len(st.session_state.ai_taste_recommendations))
                
                for idx, rec_song in enumerate(st.session_state.ai_taste_recommendations):
                    rec_track = fetch_live_track_info(rec_song['title'], rec_song['artist'], "AI Matching")
                    reason_rec = rec_song.get('reason', 'เหมาะกับแนวเพลงที่คุณชอบฟัง')
                    
                    with rec_cols[idx % len(rec_cols)]:
                        st.markdown(f"""
                        <div class="spotify-card">
                            <div>
                                <div class="spotify-card-img-wrapper">
                                    <img src="{rec_track['cover']}" class="spotify-card-img" alt="Cover">
                                </div>
                                <div class="spotify-card-title">{rec_track['name']}</div>
                                <div class="spotify-card-subtitle">{rec_track['artist']}</div>
                                <div style="font-size:0.83rem; color:#e0e0e0; margin-top:8px; line-height:1.45; word-wrap: break-word;">
                                    <strong style="color:#1DB954;">💡 คำแนะนำจาก DJ:</strong> {reason_rec}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        r_col1, r_col2 = st.columns([1.2, 0.8])
                        with r_col1:
                            if st.button("▶️ ฟังตัวอย่าง", key=f"rec_play_{idx}", use_container_width=True):
                                st.session_state.current_preview_url = rec_track['preview']
                                st.session_state.current_track_name = rec_track['name']
                                st.rerun()
                        with r_col2:
                            is_fav = any(f['name'] == rec_track['name'] for f in st.session_state.favorites)
                            if st.button("❤️" if is_fav else "🤍", key=f"rec_fav_{idx}", use_container_width=True):
                                track_dict = {
                                    'id': rec_track.get('id'),
                                    'name': rec_track['name'],
                                    'artist': rec_track['artist'],
                                    'album_cover': rec_track['cover'],
                                    'preview_url': rec_track.get('preview'),
                                    'spotify_url': rec_track['spotify_url'],
                                    'reason': rec_song.get('reason', '')
                                }
                                handle_like_song(track_dict, mood_prompt="AI วิเคราะห์จาก Audio Features")
                                st.rerun()

    else:
        if analysis_source == "❤️ เพลงในรายการโปรด":
            st.info("💡 ยังไม่มีเพลงในรายการโปรด! กรุณากดหัวใจ ❤️ ที่การ์ดเพลงในหน้าต่างๆ เพื่อเพิ่มเพลงเข้าในรายการโปรด แล้วกลับมาวิเคราะห์รสนิยมดนตรีได้เลยครับ")
        else:
            st.info("💡 ยังไม่มีเพลงจาก AI DJ! กรุณาสร้างเพลย์ลิสต์ในหน้า 'AI DJ Studio' ก่อน เพื่อดูการวิเคราะห์สถิติและรสนิยม")

# ------------------------------------------
# PAGE 4: ❤️ เพลงโปรด & ประวัติ
# ------------------------------------------
elif nav_choice == "❤️ เพลงโปรด & ประวัติ":
    st.subheader("❤ เพลงโปรดที่คุณบันทึกไว้")
    if len(st.session_state.favorites) > 0:
        fav_cols = st.columns(3)
        for idx, fav_track in enumerate(st.session_state.favorites):
            track_cover = fav_track.get('album_cover')
            track_preview = fav_track.get('preview_url')
            
            if not track_preview or not track_cover or track_cover == DEFAULT_COVER:
                img_url, prev_url, full_url = get_track_preview(fav_track['name'], fav_track.get('artist', ''))
                track_cover = track_cover or img_url or DEFAULT_COVER
                track_preview = track_preview or prev_url or FALLBACK_AUDIO_URL
                fav_track['album_cover'] = track_cover
                fav_track['preview_url'] = track_preview

            with fav_cols[idx % 3]:
                st.markdown(f"""
                <div class="spotify-card">
                    <div>
                        <div class="spotify-card-img-wrapper">
                            <img src="{track_cover}" class="spotify-card-img" alt="Album Cover">
                        </div>
                        <div class="spotify-card-title">{fav_track['name']}</div>
                        <div class="spotify-card-subtitle">{fav_track.get('artist', 'Unknown Artist')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                f_col1, f_col2, f_col3 = st.columns([1.2, 0.8, 1])
                with f_col1:
                    if st.button("▶️ ฟังเพลงนี้", key=f"fav_play_page_{idx}", use_container_width=True):
                        st.session_state.current_preview_url = track_preview
                        st.session_state.current_track_name = fav_track['name']
                        st.rerun()
                
                with f_col2:
                    if st.button("🗑", key=f"fav_remove_{idx}", use_container_width=True):
                        handle_like_song(fav_track)
                        st.rerun()

                with f_col3:
                    st.link_button("🎶 Streaming", fav_track.get('spotify_url', '#'), use_container_width=True)
    else:
        st.caption("ยังไม่มีเพลงโปรด กดหัวใจ ❤️ ที่การ์ดเพลงในหน้าต่างๆ เพื่อเพิ่มไว้ที่นี่ได้เลย")

    st.divider()
    st.subheader("📜 ประวัติการใช้งานย้อนหลัง")
    if len(st.session_state.history) > 0:
        for item in st.session_state.history:
            with st.expander(f"🕒 {item['time']} | {item['mood'][:40]}..."):
                st.write(f"**สไตล์/คาแรกเตอร์:** {item.get('persona', '-')}")
                st.write(f"**รายละเอียดอารมณ์:** {item.get('mood', '-')}")
                if item.get('playlist'):
                    st.write("**รายการเพลงที่เคยแนะนำ:**")
                    for s in item['playlist']:
                        st.write(f"- {s['name']} - {s['artist']}")
    else:
        st.caption("ยังไม่มีประวัติการจัดเพลย์ลิสต์ในระบบ")

# ==========================================
# 8. Floating Liquid Glass Music Player
# ==========================================
active_player_playlist = []

if st.session_state.playlist:
    for track in st.session_state.playlist:
        if track.get('preview_url'):
            active_player_playlist.append({
                "title": track.get('name', 'Unknown'),
                "artist": track.get('artist', 'Unknown Artist'),
                "cover": track.get('album_cover', DEFAULT_COVER),
                "url": track.get('preview_url')
            })

if st.session_state.current_preview_url:
    start_idx = 0
    found = False
    for idx, track_item in enumerate(active_player_playlist):
        if track_item['url'] == st.session_state.current_preview_url:
            start_idx = idx
            found = True
            break
    
    if not found:
        standalone_track = {
            "title": st.session_state.current_track_name or "Unknown Track",
            "artist": "DJ Moody Stream",
            "cover": DEFAULT_COVER,
            "url": st.session_state.current_preview_url
        }
        active_player_playlist.insert(0, standalone_track)
        start_idx = 0

    render_liquid_music_player(playlist=active_player_playlist, start_index=start_idx, autoplay=True)
