import streamlit as st
from ytmusicapi import YTMusic
import requests
import time

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Vibe Music", layout="centered", page_icon="🎵")

# --- INITIALIZE API ---
@st.cache_resource
def load_api():
    return YTMusic()

yt = load_api()

# --- CUSTOM CSS (Simple & Clean) ---
st.markdown("""
<style>
    /* Dark Theme */
    .stApp { background-color: #000000; color: white; }
    .stTextInput > div > div > input { 
        background-color: #1a1a1a; color: white; border-radius: 25px; 
        border: 1px solid #333; 
    }
    
    /* Song List Styling */
    .song-row {
        background: #121212; padding: 10px; border-radius: 10px; margin-bottom: 8px;
        display: flex; align-items: center; border: 1px solid #222;
    }
    .song-row:active { background: #222; }

    /* Hide Header/Footer */
    header, footer {visibility: hidden;}
    
    /* Player Styling */
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

# --- 🚀 ROBUST AUDIO ENGINE (The Fix) ---
@st.cache_data(show_spinner=False, ttl=600)
def get_audio_url(video_id):
    """
    Ye function 5 alag-alag servers try karega.
    Agar ek fail hua to dusra chalega.
    """
    # Servers List (Backup ke saath)
    instances = [
        "https://pipedapi.kavin.rocks",
        "https://api.piped.io", 
        "https://pipedapi.tokhmi.xyz",
        "https://pipedapi.moomoo.me",
        "https://pipedapi.syncpundit.io"
    ]
    
    for base_url in instances:
        try:
            # API Call
            url = f"{base_url}/streams/{video_id}"
            resp = requests.get(url, timeout=3) # 3 sec wait karega
            
            if resp.status_code == 200:
                data = resp.json()
                # Sirf Audio dhunde
                for stream in data['audioStreams']:
                    # M4A format phone ke liye best hai
                    if stream['mimeType'] == 'audio/mp4':
                        return stream['url']
        except:
            continue # Agla server try karo
            
    return None

# --- UI LOGIC ---

# >>> PLAYER SCREEN <<<
if st.session_state.page == 'player':
    song = st.session_state.current_song
    
    # Back Button
    if st.button("⬅ Back to Search"):
        st.session_state.page = 'home'
        st.rerun()

    st.markdown("<div class='player-box'>", unsafe_allow_html=True)
    
    # Album Art
    try: img = song['thumbnails'][-1]['url']
    except: img = "https://via.placeholder.com/300"
    st.image(img, width=250)
    
    # Song Title
    st.markdown(f"### {song['title']}")
    try: st.caption(song['artists'][0]['name'])
    except: pass
    
    st.write("") # Gap

    # --- AUDIO LOADING ---
    with st.spinner("🔄 Loading Audio (Connecting to Server)..."):
        audio_url = get_audio_url(song['videoId'])
        
        if audio_url:
            # Final Audio Player
            st.audio(audio_url, format='audio/mp4', start_time=0)
            st.caption("✅ Ready to Play!")
        else:
            st.error("⚠️ Server Busy. Please try another song.")
            
    st.markdown("</div>", unsafe_allow_html=True)

# >>> HOME SCREEN <<<
else:
    st.title("Vibe Music 🎧")
    
    # Search Bar
    query = st.text_input("", placeholder="Search Song Name...", value=st.session_state.search_query)

    if query:
        st.session_state.search_query = query
        
        # Search Results
        try:
            results = yt.search(query, filter="songs")[:10]
            
            if not results:
                st.warning("No songs found.")
            
            for song in results:
                # Safe Data Extraction
                title = song.get('title', 'Unknown')
                try: artist = song['artists'][0]['name']
                except: artist = "Artist"
                try: thumb = song['thumbnails'][0]['url'] 
                except: thumb = ""
                
                # List UI
                c1, c2, c3 = st.columns([1, 4, 1.5])
                with c1: st.image(thumb, width=50)
                with c2: 
                    st.write(f"**{title}**")
                    st.caption(artist)
                with c3:
                    if st.button("▶ Play", key=f"p_{song['videoId']}"):
                        st.session_state.current_song = song
                        st.session_state.page = 'player'
                        st.rerun()
                st.markdown("<hr style='margin: 5px 0; border-color: #333;'>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Search Error: {e}")

    # Trending (Agar search khali hai)
    else:
        st.subheader("🔥 Trending Now")
        trends = ["Arjan Vailly", "Chaleya", "Soft Music", "Punjabi Hits"]
        cols = st.columns(2)
        for i, t in enumerate(trends):
            with cols[i % 2]:
                if st.button(t, key=f"t_{i}", use_container_width=True):
                    st.session_state.search_query = t
                    st.rerun()



                #python -m streamlit run music.py


