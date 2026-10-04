import plotly.graph_objects as go
from freqblog_service import get_audio_features

def create_radar_chart(tracks_data):
    """สร้างกราฟ Radar สรุปภาพรวมอารมณ์เพลงทั้ง Playlist โดยดึงค่าจาก FreqBlog API"""
    if not tracks_data:
        return None
        
    categories = [
        "Energy (ความคึกคัก)",
        "Valence (ความสุข/อารมณ์บวก)",
        "Danceability (จังหวะน่าเต้น)",
        "Acousticness (ความเป็นอะคูสติก)"
    ]
    
    total_energy = 0.0
    total_valence = 0.0
    total_danceability = 0.0
    total_acousticness = 0.0
    count = 0

    for track in tracks_data:
        title = track.get('name') or track.get('title', '')
        artist = track.get('artist', '')
        spotify_id = track.get('id') or track.get('spotify_id', None)

        if not title:
            continue

        # ดึง Audio Features จาก FreqBlog API
        features = get_audio_features(title, artist, spotify_id)
        
        total_energy += features.get('energy', 0.5)
        total_valence += features.get('valence', 0.5)
        total_danceability += features.get('danceability', 0.5)
        total_acousticness += features.get('acousticness', 0.5)
        count += 1

    if count == 0:
        return None

    avg_values = [
        total_energy / count,
        total_valence / count,
        total_danceability / count,
        total_acousticness / count
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=avg_values,
        theta=categories,
        fill='toself',
        name='Playlist Profile',
        fillcolor='rgba(29, 185, 84, 0.35)',
        line=dict(color='#1DB954', width=2)
    ))

    fig.update_layout(
        title="📊 ภาพรวมอารมณ์ของ Playlist นี้ (วิเคราะห์โดย FreqBlog)",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                color='#ffffff',
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            angularaxis=dict(
                color='#ffffff',
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            bgcolor='rgba(0, 0, 0, 0)'
        ),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='#ffffff', family='Prompt, sans-serif'),
        showlegend=False,
        margin=dict(l=40, r=40, t=50, b=30)
    )

    return fig