import os

def get_playlist_from_ai(prompt: str):
    """
    ฟังก์ชันรับคำขอ (prompt) แล้วส่งไปประมวลผลกับ AI เพื่อคืนค่า Playlist
    """
    try:
        # TODO: ใส่โค้ดเชื่อมต่อกับ AI API ของคุณที่นี่ (เช่น OpenAI, Gemini หรืออื่นๆ)
        # ตัวอย่างโครงสร้างการส่งคืนข้อมูล:
        
        playlist = [
            {"title": "Song 1", "artist": "Artist A"},
            {"title": "Song 2", "artist": "Artist B"},
            {"title": "Song 3", "artist": "Artist C"},
        ]
        
        return playlist

    except Exception as e:
        print(f"Error: {e}")
        return []
