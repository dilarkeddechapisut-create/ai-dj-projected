import plotly.express as px
import pandas as pd

def create_radar_chart(tracks_data):
    """สร้างกราฟ Radar สรุปภาพรวมอารมณ์เพลงทั้ง Playlist"""
    if not tracks_data:
        return None
        
    df = pd.DataFrame(tracks_data)
    
    # หาค่าเฉลี่ยของคุณลักษณะเพลง
    avg_stats = {
        "Energy (ความคึกคัก)": df['energy'].mean(),
        "Valence (ความสุข)": df['valence'].mean(),
        "Danceability (จังหวะเต้น)": df['danceability'].mean()
    }
    
    radar_df = pd.DataFrame(dict(
        r=list(avg_stats.values()),
        theta=list(avg_stats.keys())
    ))
    
    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True, 
                        title="📊 ภาพรวมอารมณ์ของ Playlist นี้",
                        template="plotly_dark",
                        color_discrete_sequence=['#1DB954']) # สีเขียว Spotify
    fig.update_traces(fill='toself')
    
    return fig