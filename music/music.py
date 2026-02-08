import streamlit as st
from ytmusicapi import YTMusic
import requests

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Vibe Music", layout="centered", page_icon="🎵")

# --- INITIALIZE API ---
@st.cache_resource
def load_api():
    return YTMusic()

yt = load_api()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: white; }
    .stTextInput > div > div > input { 
        background-color: #1a1a1a; color: white; border-radius: 25px; 
        border: 1px solid #333; 
    }
    .song-row {
        background: #121212; padding: 10px; border-radius: 10px; margin-bottom: 8px;
        display: flex; align-items: center; border: 1px solid #222;
    }
    header, footer {visibility: hidden;}
    .player-box {
        background: #111; padding: 20px; border-radius: 15px; 
        text-align: center; border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'current_song' not in st.session_state: st.session_state.current_song = None
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# --- SMART ENGINE (Audio First -> Video Backup) ---
@st.cache_data(show_spinner=False, ttl=600)
def get_audio_url(video_id):
    # Fake User-Agent taaki server ko lage hum browser hain
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    instances = [
        "https://pipedapi.kavin.rocks",
        "https://api.piped.io", 
        "https://pipedapi.tokhmi.xyz",
        "https://pipedapi.moomoo.me"
    ]
    
    for base_url in instances:
        try:
            url = f"{base_url}/streams/{video_id}"
            resp = requests.get(url, headers=headers, timeout=2) 
            if resp.status_code == 200:
                data = resp.json()
                for stream in data['audioStreams']:
                    if stream['mimeType'] == 'audio/mp4':
                        return stream['url']
        except:
            continue
    return None

# --- UI LOGIC ---

if st.session_state.page == 'player':
    song = st.session_state.current_song
    
    if st.button("⬅ Back"):
        st.session_state.page = 'home'
        st.rerun()

    st.markdown("<div class='player-box'>", unsafe_allow_html=True)
    
    # Image
    try: img = song['thumbnails'][-1]['url']
    except: img = ""
    st.image(img, width=250)
    
    st.markdown(f"### {song['title']}")
    try: st.caption(song['artists'][0]['name'])
    except: pass
    
    st.write("")

    # --- HYBRID PLAYER LOGIC ---
    # Step 1: Try Audio
    with st.spinner("Connecting..."):
        audio_url = get_audio_url(song['videoId'])

    if audio_url:
        # Agar Server Theek Hai -> Audio Bajao
        st.audio(audio_url, format='audio/mp4', start_time=0)
        st.caption("✅ High Quality Audio")
    else:
        # Agar Server Busy Hai -> AUTOMATIC Backup (Video Player)
        # Error dikhane ki jagah seedha play kar dega
        st.caption("⚠️ Audio Server Busy -> Switching to Direct Mode")
        st.video(f"https://www.youtube.com/watch?v={song['videoId']}")
        st.caption("ℹ️ Background play ke liye Brave/Firefox browser use karein.")
            
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.title("Vibe Music 🎵")
    query = st.text_input("", placeholder="Search song...", value=st.session_state.search_query)

    if query:
        st.session_state.search_query = query
        try:
            results = yt.search(query, filter="songs")[:10]
            for song in results:
                title = song.get('title', 'Track')
                try: artist = song['artists'][0]['name']
                except: artist = ""
                try: thumb = song['thumbnails'][0]['url'] 
                except: thumb = ""
                
                c1, c2, c3 = st.columns([1, 4, 1.5])
                with c1: st.image(thumb, width=50)
                with c2: 
                    st.write(f"**{title}**")
                    st.caption(artist)
                with c3:
                    if st.button("▶", key=f"p_{song['videoId']}"):
                        st.session_state.current_song = song
                        st.session_state.page = 'player'
                        st.rerun()
                st.markdown("<hr style='margin: 5px 0; border-color: #333;'>", unsafe_allow_html=True)
        except: st.error("Search failed.")
    
    else:
        st.subheader("🔥 Quick Play")
        trends = ["Arjan Vailly", "Chaleya", "Punjabi Hits", "LoFi"]
        cols = st.columns(2)
        for i, t in enumerate(trends):
            with cols[i % 2]:
                if st.button(t, key=f"t_{i}", use_container_width=True):
                    st.session_state.search_query = t
                    st.rerun()



                #python -m streamlit run music.py



