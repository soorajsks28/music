import streamlit as st
from ytmusicapi import YTMusic
import yt_dlp

# --- APP CONFIGURATION (Fast Load) ---
st.set_page_config(page_title="Vibe Music", layout="centered", page_icon="🎵")

# --- INITIALIZE API ---
@st.cache_resource
def load_api():
    return YTMusic()

yt = load_api()

# --- CUSTOM CSS (Spotify Dark Theme + Fast UI) ---
st.markdown("""
<style>
    /* 1. Ultra Dark Theme */
    .stApp {
        background-color: #000000;
        color: white;
    }
    
    /* 2. Search Bar (Google Style) */
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: white;
        border-radius: 30px;
        padding: 10px 20px;
        border: 1px solid #333;
        font-size: 16px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1DB954; /* Spotify Green */
    }

    /* 3. Song List Item (Compact & Fast) */
    .song-row {
        background: #121212;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        transition: 0.2s;
        border: 1px solid transparent;
    }
    .song-row:hover {
        background: #2a2a2a;
        border-color: #1DB954;
    }

    /* 4. Suggestion Chips */
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 20px;
        border: 1px solid #333;
        background-color: #1a1a1a;
        color: white;
        font-size: 12px;
        padding: 2px 10px;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        border-color: #1DB954;
        color: #1DB954;
    }

    /* Hide Extra Streamlit Junk */
    header, footer {visibility: hidden;}
    
    /* Player Overlay */
    .player-box {
        background: linear-gradient(180deg, rgba(30,30,30,1) 0%, rgba(0,0,0,1) 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'current_song' not in st.session_state: st.session_state.current_song = None
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# --- ULTRA FAST FUNCTIONS ---

@st.cache_data(ttl=3600, show_spinner=False)
def get_search_suggestions(query):
    # Google/YouTube like suggestions
    try: return yt.get_search_suggestions(query)[:4]
    except: return []

@st.cache_data(ttl=3600, show_spinner=False)
def search_tracks(query):
    # Search Results Cache (Speed Booster)
    return yt.search(query, filter="songs")[:15]

@st.cache_data(show_spinner=False)
def get_audio_url(video_id):
    # Extracts Audio Link
    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)['url']
    except: return None

# --- UI LOGIC ---

# >>> PLAYER SCREEN <<<
if st.session_state.page == 'player':
    song = st.session_state.current_song
    
    # Back Button (Spotify Style Top-Left)
    if st.button("⬅ Back", key="back_btn"):
        st.session_state.page = 'home'
        st.rerun()

    # Player UI
    st.markdown("<div class='player-box'>", unsafe_allow_html=True)
    
    col_art, col_info = st.columns([1, 1])
    with col_art:
        try: img = song['thumbnails'][-1]['url']
        except: img = "https://via.placeholder.com/300"
        st.image(img, use_container_width=True)
        
    with col_info:
        st.markdown(f"### {song['title']}")
        try: st.caption(song['artists'][0]['name'])
        except: st.caption("Unknown Artist")
        
        # Audio loading...
        with st.spinner("Connecting to Server..."):
            url = get_audio_url(song['videoId'])
            if url:
                st.audio(url, format='audio/mp3', start_time=0)
            else:
                st.error("Audio unavailable.")
                
    st.markdown("</div>", unsafe_allow_html=True)

# >>> HOME / SEARCH SCREEN <<<
else:
    st.title("Vibe Music 🎵")
    
    # 1. SEARCH BAR (The Brain)
    # Note: Streamlit requires 'Enter' key to submit
    new_query = st.text_input("", placeholder="Search songs, artists, or moods...", value=st.session_state.search_query)

    if new_query:
        st.session_state.search_query = new_query
        
        # 2. SUGGESTIONS (Google Style Chips)
        suggs = get_search_suggestions(new_query)
        if suggs:
            st.caption("Did you mean?")
            cols = st.columns(len(suggs))
            for i, sugg in enumerate(suggs):
                with cols[i]:
                    if st.button(sugg, key=f"s_{i}"):
                        st.session_state.search_query = sugg
                        st.rerun()

        # 3. RESULTS LIST (Spotify Style)
        st.markdown("---")
        results = search_tracks(st.session_state.search_query)
        
        for song in results:
            # Clean Data
            title = song.get('title', 'Track')
            try: artist = song['artists'][0]['name']
            except: artist = "Artist"
            try: thumb = song['thumbnails'][0]['url'] # Small thumb for speed
            except: thumb = ""
            vid_id = song['videoId']

            # Compact Row
            c1, c2, c3 = st.columns([1, 5, 1])
            with c1:
                st.image(thumb, width=50)
            with c2:
                st.markdown(f"<div style='margin-top: 5px; font-weight: bold;'>{title}</div>", unsafe_allow_html=True)
                st.caption(artist)
            with c3:
                # PLAY BUTTON
                if st.button("▶", key=f"p_{vid_id}"):
                    st.session_state.current_song = song
                    st.session_state.page = 'player'
                    st.rerun()
            
            st.markdown("<div style='border-bottom: 1px solid #222; margin-bottom: 5px;'></div>", unsafe_allow_html=True)

    # 4. DEFAULT HOME (If Search is Empty)
    else:
        st.subheader("🚀 Quick Picks")
        
        # Fast Mood Buttons
        moods = ["Trending India", "Punjabi Hits", "LoFi Beats", "Gym Phonk", "90s Bollywood"]
        m_cols = st.columns(3)
        for i, mood in enumerate(moods):
            with m_cols[i % 3]:
                if st.button(mood, key=f"m_{i}", use_container_width=True):
                    st.session_state.search_query = mood
                    st.rerun()


                #python -m streamlit run music.py