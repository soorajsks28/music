import streamlit as st
from ytmusicapi import YTMusic
import requests  # Data fetch karne ke liye

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
    /* 1. Ultra Dark Theme */
    .stApp { background-color: #000000; color: white; }
    
    /* 2. Search Bar */
    .stTextInput > div > div > input {
        background-color: #1a1a1a; color: white; border-radius: 30px; 
        border: 1px solid #333; font-size: 16px;
    }
    
    /* 3. Song List */
    .song-row {
        background: #121212; padding: 10px; border-radius: 8px; margin-bottom: 5px;
        display: flex; align-items: center; border: 1px solid transparent;
    }
    .song-row:hover { border-color: #1DB954; }

    /* Hide Junk */
    header, footer {visibility: hidden;}
    
    /* Player Box */
    .player-box {
        background: linear-gradient(180deg, rgba(30,30,30,1) 0%, rgba(0,0,0,1) 100%);
        padding: 20px; border-radius: 15px; text-align: center; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'current_song' not in st.session_state: st.session_state.current_song = None
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# --- NEW AUDIO ENGINE (BYPASS) ---
@st.cache_data(show_spinner=False, ttl=600)
def get_audio_stream(video_id):
    """
    Piped API ka use karke direct Audio Stream nikalta hai.
    Ye YouTube Blocking ko bypass karta hai.
    """
    # Public Instances ki list (agar ek down ho to dusra try kare)
    instances = [
        "https://pipedapi.kavin.rocks",
        "https://api.piped.io",
        "https://pipedapi.kavin.rocks"
    ]
    
    for base_url in instances:
        try:
            url = f"{base_url}/streams/{video_id}"
            response = requests.get(url, timeout=4)
            data = response.json()
            
            # Sirf Audio streams dhundo
            for stream in data['audioStreams']:
                # M4A format sabse badhiya chalta hai browsers mein
                if stream['mimeType'] == 'audio/mp4':
                    return stream['url']
        except:
            continue
            
    return None

# --- UI LOGIC ---

# >>> PLAYER SCREEN <<<
if st.session_state.page == 'player':
    song = st.session_state.current_song
    
    if st.button("⬅ Back", key="back_btn"):
        st.session_state.page = 'home'
        st.rerun()

    # Player UI
    st.markdown("<div class='player-box'>", unsafe_allow_html=True)
    
    # Album Art
    try: img = song['thumbnails'][-1]['url']
    except: img = "https://via.placeholder.com/300"
    st.image(img, use_container_width=True)
    
    # Details
    st.markdown(f"### {song['title']}")
    try: st.caption(song['artists'][0]['name'])
    except: st.caption("Unknown Artist")
    
    st.write("") # Spacer
    
    # --- AUDIO PLAYER (FIXED) ---
    with st.spinner("🎧 Fetching best audio stream..."):
        audio_url = get_audio_stream(song['videoId'])
        
        if audio_url:
            # Format 'audio/mp4' use karein taaki Android background mein play kare
            st.audio(audio_url, format='audio/mp4', start_time=0)
            st.caption("✅ Audio Loaded (Background Play Supported)")
        else:
            st.error("⚠️ Stream not found. Try another song.")
            # Fallback Video (sirf agar audio fail ho)
            st.video(f"https://www.youtube.com/watch?v={song['videoId']}")
            
    st.markdown("</div>", unsafe_allow_html=True)

# >>> HOME SCREEN <<<
else:
    st.title("Vibe Music 🎵")
    
    query = st.text_input("", placeholder="Search song...", value=st.session_state.search_query)

    if query:
        st.session_state.search_query = query
        
        # Results
        try:
            results = yt.search(query, filter="songs")[:10]
            for song in results:
                title = song.get('title', 'Track')
                try: artist = song['artists'][0]['name']
                except: artist = "Artist"
                try: thumb = song['thumbnails'][0]['url'] 
                except: thumb = ""
                
                c1, c2, c3 = st.columns([1, 5, 1])
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
        except:
            st.error("Search failed.")

    else:
        st.subheader("🔥 Quick Play")
        moods = ["Arjan Vailly", "Chaleya", "Punjabi Hits", "LoFi"]
        cols = st.columns(2)
        for i, m in enumerate(moods):
            with cols[i % 2]:
                if st.button(m, key=f"m_{i}", use_container_width=True):
                    st.session_state.search_query = m
                    st.rerun()



                #python -m streamlit run music.py

