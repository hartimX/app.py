import streamlit as st
import requests
import math
import random

# --- API ANAHTARLARI ---
OMDB_API_KEY = "230D910E"
TMDB_API_KEY = "ffa196d9c44790c7864d5aa4a06ca623"

# Sayfa Yapılandırması
st.set_page_config(page_title="The Hartim Curve", page_icon="⚖️", layout="wide")

# --- HAFIZA YÖNETİMİ ---
if 'watched_movies' not in st.session_state: st.session_state.watched_movies = []
if 'current_movie_id' not in st.session_state: st.session_state.current_movie_id = ""
if 'search_query' not in st.session_state: st.session_state.search_query = ""

def get_random_horror():
    page = random.randint(1, 15)
    # Sadece belli bir popülarite üzerindeki (vote_count > 100) korku filmleri
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres=27&vote_count.gte=100&page={page}"
    res = requests.get(url).json()
    if res.get("results"):
        movies = res['results']
        if st.session_state.get('filter_watched', True):
            movies = [m for m in movies if m['title'] not in st.session_state.watched_movies]
        
        if movies:
            chosen = random.choice(movies)
            # Kritik Nokta: İsmi değil, ID'yi kaydediyoruz!
            st.session_state.current_movie_id = chosen.get("id")
            st.session_state.search_query = chosen.get("title")

# Görsel Stil (Premium Tasarım)
st.markdown("""
    <style>
    ::-webkit-scrollbar { display: none; }
    html, body { -ms-overflow-style: none; scrollbar-width: none; background-color: #000000; }
    .main { background-color: #000000; color: white; }
    h1 { color: #ff0000; text-align: center; font-weight: 900; letter-spacing: -2px; }
    .slogan { text-align: center; color: #adb5bd; margin-bottom: 20px; }
    .stTextInput input { color: #ffffff !important; background-color: #1a1c23; border: 2px solid #ff0000; border-radius: 5px; }
    .metric-card { background-color: #1a1c23; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #2d3139; color: #ffffff; }
    .hartim-box { background-color: #1a1c23; padding: 30px; border-radius: 20px; border-left: 10px solid #ff4b4b; box-shadow: 0 10px 30px rgba(255,0,0,0.2); }
    .sub-genre-tag { background-color: #ff0000; color: white; padding: 2px 8px; border-radius: 5px; font-size: 12px; margin-right: 5px; font-weight: bold; text-transform: uppercase; }
    [data-testid="stSidebar"] { background-color: #0b0d11; border-right: 1px solid #2d3139; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff0000;'>🎬 Korku Arşivi</h2>", unsafe_allow_html=True)
    st.checkbox("İzlediklerimi Önerme", value=True, key="filter_watched")
    st.divider()
    for m in reversed(st.session_state.watched_movies):
        st.markdown(f"- <small style='color: #ffffff;'>{m}</small>", unsafe_allow_html=True)

st.title("THE HARTIM CURVE")
st.markdown("<p class='slogan'>Gizli Korku Cevherlerini Keşfet</p>", unsafe_allow_html=True)

col_search, col_btn = st.columns([4, 1.2])
with col_search:
    st.text_input("", placeholder="Korku filmi yazın...", key="search_query")
with col_btn:
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.button("Bana Korku Öner 🎲", use_container_width=True, on_click=get_random_horror)

# --- VERİ ÇEKME MOTORU (ID veya İSİM) ---
target = st.session_state.search_query
if target:
    # Eğer öneri butonuna basılmışsa ID ile, arama yapılmışsa isimle TMDb'den IMDb ID'sini alıyoruz
    if st.session_state.current_movie_id:
        tmdb_url = f"https://api.themoviedb.org/3/movie/{st.session_state.current_movie_id}?api_key={TMDB_API_KEY}"
    else:
        tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={target}"
    
    t_data = requests.get(tmdb_url).json()
    
    # ID Köprüsü Kuruluyor
    movie_id = ""
    if st.session_state.current_movie_id:
        movie_id = t_data.get("imdb_id")
    elif t_data.get("results"):
        # Arama sonucunda en üstteki filmin detayına gidip IMDb ID'sini alıyoruz
        detail_url = f"https://api.themoviedb.org/3/movie/{t_data['results'][0]['id']}?api_key={TMDB_API_KEY}"
        movie_id = requests.get(detail_url).json().get("imdb_id")

    if movie_id:
        # OMDb'ye isimle değil, kesinleşmiş IMDb ID ile soruyoruz!
        omdb_url = f"http://www.omdbapi.com/?i={movie_id}&apikey={OMDB_API_KEY}"
        o_data = requests.get(omdb_url).json()

        if o_data.get("Response") == "True" and "Horror" in o_data.get("Genre", ""):
            title = o_data.get("Title")
            poster = o_data.get("Poster")
            genres = o_data.get("Genre", "").split(", ")
            plot = o_data.get("Plot", "").lower()
            
            # Alt Tür (Sub-genre) Analiz Motoru
            sub_tags = []
            if any(x in plot for x in ["ghost", "demon", "paranormal", "haunt"]): sub_tags.append("Supernatural")
            if any(x in plot for x in ["killer", "slasher", "mask", "serial"]): sub_tags.append("Slasher")
            if any(x in plot for x in ["alien", "space", "sci-fi"]): sub_tags.append("Sci-Fi Horror")
            if any(x in plot for x in ["gore", "body", "mutation", "flesh"]): sub_tags.append("Body Horror")
            if any(x in plot for x in ["psychological", "mind", "insanity"]): sub_tags.append("Psychological")

            # Puanlar ve Kalkan (Aynı Mantık)
            p_imdb = float(o_data.get("imdbRating", 0)) if o_data.get("imdbRating") != "N/A" else 0
            p_meta = int(o_data.get("Metascore")) / 10 if o_data.get("Metascore") != "N/A" else 0
            p_tomato = 0
            for r in o_data.get("Ratings", []):
                if r['Source'] == 'Rotten Tomatoes': p_tomato = int(r['Value'].replace('%', '')) / 10
            
            # TMDb puanını doğrudan çekiyoruz
            p_tmdb = t_data.get("vote_average", 0) if st.session_state.current_movie_id else t_data['results'][0].get("vote_average", 0)

            H = (p_imdb + p_tmdb) / 2
            E = (p_meta + p_tomato) / 2 if (p_meta > 0 and p_tomato > 0) else (p_meta or p_tomato)

            if H > 0 and E > 0:
                fark = H - E
                if fark >= 2.5: B = (H * 0.90) + (E * 0.10)
                elif fark >= 1.5: B = (H * 0.75) + (E * 0.25)
                else: B = (H * 0.50) + (E * 0.50)
            else: B = H or E

            bonus = 0.85 * math.exp(-((B - 6.75)**2) / (2 * 1.8**2))
            h_score = min(B + bonus, 10.0)

            # Arayüz Çizimi
            st.divider()
            col1, col2 = st.columns([1, 1.5])
            with col1: st.image(poster if poster != "N/A" else "https://via.placeholder.com/300x450")
            with col2:
                st.header(title)
                # Alt Tür Etiketlerini Basıyoruz
                tag_html = "".join([f"<span class='sub-genre-tag'>{t}</span>" for t in sub_tags])
                st.markdown(tag_html, unsafe_allow_html=True)
                
                m1, m2, m3, m4 = st.columns(4)
                m1.markdown(f"<div class='metric-card'><small>IMDb</small><br><b>{p_imdb}</b></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-card'><small>Meta</small><br><b>{p_meta}</b></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-card'><small>Tomato</small><br><b>{p_tomato}</b></div>", unsafe_allow_html=True)
                m4.markdown(f"<div class='metric-card'><small>TMDb</small><br><b>{p_tmdb:.1f}</b></div>", unsafe_allow_html=True)

                st.markdown(f"<div class='hartim-box'><small>THE HARTIM EQUATION RESULT</small><h1 style='text-align: left; color: #ff4b4b; font-size: 80px;'>{h_score:.2f}</h1></div>", unsafe_allow_html=True)
                
                if st.button("✅ Bu Filmi İzledim Arşive Ekle", use_container_width=True):
                    if title not in st.session_state.watched_movies:
                        st.session_state.watched_movies.append(title)
                        st.rerun()
            
            # Her işlem sonunda ID'yi sıfırla ki bir sonraki arama temiz olsun
            st.session_state.current_movie_id = ""
        else:
            st.error("🛑 Uyarı: Bu bir korku filmi değil veya sistem eşleşme sağlayamadı.")
