import pandas as pd
import plotly.graph_objects as go
import requests
import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyClientCredentials

# ---------------------------------------------------------
# 1. การตั้งค่าหน้าจอ และ Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="AI DJ & Music Analytics", layout="wide")
st.title("🎵 AI DJ - Music Analytics (FreqBlog API Integration)")

# อ่าน Credentials จาก st.secrets หรือกำหนดค่า
SPOTIPY_CLIENT_ID = st.secrets.get("SPOTIFY_CLIENT_ID", "YOUR_SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = st.secrets.get(
    "SPOTIFY_CLIENT_SECRET", "YOUR_SPOTIFY_CLIENT_SECRET"
)
FREQBLOG_API_KEY = st.secrets.get(
    "FREQBLOG_API_KEY", ""
)  # หากไม่มี สามารถเว้นว่างไว้ทดลองใช้ Free Tier ได้


# Initialize Spotify Client
@st.cache_resource
def get_spotify_client():
    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
    )
    return spotipy.Spotify(auth_manager=auth_manager)


sp = get_spotify_client()


# ---------------------------------------------------------
# 2. ฟังก์ชันดึง Audio Features จาก FreqBlog API
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_freqblog_features(artist_name: str, track_name: str) -> dict:
    """ดึงค่า Audio Features (BPM, Energy, Danceability, Valence, Key) จาก FreqBlog API โดยใช้ชื่อศิลปินและชื่อเพลง"""
    url = "https://api.freqblog.com/lookup"
    params = {"artist": artist_name, "track": track_name}
    headers = {}

    if FREQBLOG_API_KEY:
        headers["X-Api-Key"] = FREQBLOG_API_KEY

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "bpm": data.get("bpm", 0),
                "energy": data.get("energy", 0.0),
                "danceability": data.get("danceability", 0.0),
                "valence": data.get("valence", 0.0),
                "acousticness": data.get("acousticness", 0.0),
                "key": data.get("key", "N/A"),
                "camelot": data.get("camelot", "N/A"),
            }
    except Exception as e:
        st.warning(f"ไม่สามารถดึงข้อมูลจาก FreqBlog สำหรับเพลง {track_name}: {e}")

    # Fallback กรณีหาไม่เจอหรือเกิดข้อผิดพลาด
    return {
        "bpm": None,
        "energy": None,
        "danceability": None,
        "valence": None,
        "acousticness": None,
        "key": "N/A",
        "camelot": "N/A",
    }


# ---------------------------------------------------------
# 3. ส่วนควบคุมการดึงข้อมูล Playlist
# ---------------------------------------------------------
playlist_url = st.text_input(
    "ใส่ Spotify Playlist URL หรือ Playlist ID:",
    value="https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",  # ตัวอย่าง Today's Top Hits
)

if st.button("วิเคราะห์ข้อมูลเพลงใน Playlist"):
    with st.spinner("กำลังดึงรายชื่อเพลงจาก Spotify และวิเคราะห์ Audio Features จาก FreqBlog..."):
        try:
            # ดึงข้อมูลเพลงจาก Spotify
            playlist_id = playlist_url.split("/")[-1].split("?")[0]
            results = sp.playlist_items(playlist_id, limit=20)

            tracks_data = []

            for item in results["items"]:
                track = item.get("track")
                if not track:
                    continue

                track_name = track["name"]
                artist_name = track["artists"][0]["name"]
                album_name = track["album"]["name"]

                # เรียก FreqBlog API แทน Spotify audio_features
                fb_features = fetch_freqblog_features(artist_name, track_name)

                tracks_data.append(
                    {
                        "Track": track_name,
                        "Artist": artist_name,
                        "Album": album_name,
                        "BPM": fb_features["bpm"],
                        "Energy": fb_features["energy"],
                        "Danceability": fb_features["danceability"],
                        "Valence": fb_features["valence"],
                        "Acousticness": fb_features["acousticness"],
                        "Key": fb_features["key"],
                        "Camelot": fb_features["camelot"],
                    }
                )

            df = pd.DataFrame(tracks_data)
            st.session_state["playlist_df"] = df
            st.success(f"ดึงข้อมูลสำเร็จทั้งหมด {len(df)} เพลง!")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

# ---------------------------------------------------------
# 4. การแสดงผลข้อมูล และ Radar Chart
# ---------------------------------------------------------
if "playlist_df" in st.session_state:
    df = st.session_state["playlist_df"]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 รายการเพลง และ Audio Features")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📊 สถิติวัดอารมณ์ของ Playlist (Radar Chart)")

        # คำนวณค่าเฉลี่ยของ Feature หลัก (ละเว้นค่า None)
        valid_df = df.dropna(
            subset=["Energy", "Danceability", "Valence", "Acousticness"]
        )

        if not valid_df.empty:
            avg_energy = valid_df["Energy"].mean()
            avg_dance = valid_df["Danceability"].mean()
            avg_valence = valid_df["Valence"].mean()
            avg_acoustic = valid_df["Acousticness"].mean()
            avg_bpm = valid_df["BPM"].mean()

            # สร้าง Radar Chart ด้วย Plotly
            categories = ["Energy", "Danceability", "Valence", "Acousticness"]
            values = [avg_energy, avg_dance, avg_valence, avg_acoustic]

            fig = go.Figure()
            fig.add_trace(
                go.Scatterpolar(
                    r=values + [values[0]],  # ปิดลูปวงกลม
                    theta=categories + [categories[0]],
                    fill="toself",
                    name="Playlist Average",
                    line_color="#1DB954",
                )
            )

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, range=[0, 1]
                    )  # ค่าสเกล 0 ถึง 1 ตามรูปแบบ Spotify
                ),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=20),
            )

            st.plotly_chart(fig, use_container_width=True)

            st.metric("ค่าเฉลี่ย Tempo (BPM)", f"{avg_bpm:.1f} BPM")
        else:
            st.info("ไม่พบข้อมูล Audio Features ที่สมบูรณ์สำหรับวาดกราฟ")
