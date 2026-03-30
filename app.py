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
    page = random.randint(1, 25)
    # Sadece Korku (27). Animasyon(16), Komedi(35) ve Aile(10751) filtrelenerek saf dışı bırakılır!
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres=27&without_genres=16,35,10751&vote_count.gte=50&page={page}"
    res = requests.get(url).json()
    if res.get("results"):
        movies = [m for m in res['results'] if m['title'] not in st.session_state.watched_movies]
        if movies:
            chosen = random.choice(movies)
            st.session_state.current_movie_id = chosen.get("id")
            st.session_state.search_query = chosen.get("title")

# Görsel Stil (Premium Tasarım + Kaydırma Çubuğu Gizleme)
st.markdown("""
    <style>
    ::-webkit-scrollbar { display: none; }
    html, body { -ms-overflow-style: none; scrollbar-width: none; background-color: #000000; }
    .main { background-color: #000000; color: white; }
    h1 { color: #ff0000; text-align: center; font-weight: 900; letter-spacing: -2px; margin-bottom: 0px; }
    .slogan { text-align: center; color: #adb5bd; font-size: 1.1rem; margin-top: 5px; margin-bottom: 20px; }
    .stTextInput input { color: #ffffff !important; background-color: #1a1c23; border: 2px solid #ff0000; border-radius: 5px; padding: 10px; }
    .metric-card { background-color: #1a1c23; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #2d3139; color: #ffffff; }
    .metric-card small { color: #adb5bd; }
    .hartim-box { background-color: #1a1c23; padding: 30px; border-radius: 20px; border-left: 10px solid #ff4b4b; margin-top: 20px; box-shadow: 0 10px 30px rgba(255,0,0,0.2); }
    [data-testid="stSidebar"] { background-color: #0b0d11; border-right: 1px solid #2d3139; }
    .opening-screen { text-align: center; margin-top: 100px; padding: 20px; }
    .opening-icon { font-size: 5rem; color: #ff0000; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Korku Arşivi) ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff0000;'>🎬 Korku Arşivi</h2>", unsafe_allow_html=True)
    st.checkbox("İzlediklerimi Önerme", value=True, key="filter_watched")
    st.divider()
    st.markdown("<h4 style='color: #adb5bd;'>İzlediklerim</h4>", unsafe_allow_html=True)
    for m in reversed(st.session_state.watched_movies):
        st.markdown(f"- <small style='color: #ffffff;'>{m}</small>", unsafe_allow_html=True)

st.title("THE HARTIM CURVE")
st.markdown("<p class='slogan'>Gizli Korku Cevherlerini Keşfet</p>", unsafe_allow_html=True)

# Arama ve Öneri Barı
col_search, col_btn = st.columns([4, 1.2])
with col_search:
    st.text_input("", placeholder="Korku filmi yazın...", key="search_query")
with col_btn:
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.button("Bana Korku Öner 🎲", use_container_width=True, on_click=get_random_horror)

target = st.session_state.search_query
if not target:
    st.markdown("""<div class='opening-screen'><div class='opening-icon'>🕯️</div><p style='color: #adb5bd;'>Korku Sinemasının Gerçek Terazisi seni bekliyor.</p></div>""", unsafe_allow_html=True)
else:
    # --- POPÜLERLİK ODAKLI VERİ ÇEKME MOTORU ---
    if st.session_state.current_movie_id:
        tmdb_url = f"https://api.themoviedb.org/3/movie/{st.session_state.current_movie_id}?api_key={TMDB_API_KEY}"
        t_res = requests.get(tmdb_url).json()
        movie_id = t_res.get("imdb_id")
        p_tmdb = t_res.get("vote_average", 0)
    else:
        tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={target}"
        t_search = requests.get(tmdb_url).json()
        movie_id = ""
        p_tmdb = 0
        if t_search.get("results"):
            valid_results = sorted(t_search['results'], key=lambda x: x.get('vote_count', 0), reverse=True)
            for candidate in valid_results[:5]:
                detail = requests.get(f"https://api.themoviedb.org/3/movie/{candidate['id']}?api_key={TMDB_API_KEY}").json()
                valid_genres = [g['name'] for g in detail.get('genres', [])]
                if "Horror" in valid_genres:
                    movie_id = detail.get('imdb_id')
                    p_tmdb = candidate.get("vote_average", 0)
                    break

    if movie_id:
        o_data = requests.get(f"http://www.omdbapi.com/?i={movie_id}&apikey={OMDB_API_KEY}").json()
        
        if o_data.get("Response") == "True":
            genre_str = o_data.get("Genre", "")
            invalid_genres = ["Comedy", "Animation", "Family"]
            
            # --- SAF KORKU KONTROLÜ (Hard Blacklist) ---
            if "Horror" in genre_str and not any(g in genre_str for g in invalid_genres):
                title = o_data.get("Title")
                poster = o_data.get("Poster")

                # --- AYRIŞMA PROTOKOLÜ (Divergence Shield) ---
                p_imdb = float(o_data.get("imdbRating", 0)) if o_data.get("imdbRating") != "N/A" else 0
                p_meta = int(o_data.get("Metascore")) / 10 if o_data.get("Metascore") != "N/A" else 0
                p_tomato = 0
                for r in o_data.get("Ratings", []):
                    if r['Source'] == 'Rotten Tomatoes': p_tomato = int(r['Value'].replace('%', '')) / 10

                H = (p_imdb + p_tmdb) / 2
                E = (p_meta + p_tomato) / 2 if (p_meta > 0 and p_tomato > 0) else (p_meta or p_tomato)

                if H > 0 and E > 0:
                    fark = H - E
                    if fark >= 2.5: B = (H * 0.90) + (E * 0.10)
                    elif fark >= 1.5: B = (H * 0.75) + (E * 0.25)
                    else: B = (H * 0.50) + (E * 0.50)
                else: B = H or E

                # --- THE HARTIM EQUATION ---
                h_score = min(B + (0.85 * math.exp(-((B - 6.75)**2) / (2 * 1.8**2))), 10.0)

                # --- ARAYÜZ ÇİZİMİ ---
                st.divider()
                c1, c2 = st.columns([1, 1.5])
                with c1: st.image(poster if poster != "N/A" else "https://via.placeholder.com/300x450")
                with c2:
                    st.header(title)
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.markdown(f"<div class='metric-card'><small>IMDb</small><br><b>{p_imdb}</b></div>", unsafe_allow_html=True)
                    m2.markdown(f"<div class='metric-card'><small>Meta</small><br><b>{p_meta}</b></div>", unsafe_allow_html=True)
                    m3.markdown(f"<div class='metric-card'><small>Tomato</small><br><b>{p_tomato}</b></div>", unsafe_allow_html=True)
                    m4.markdown(f"<div class='metric-card'><small>TMDb</small><br><b>{p_tmdb:.1f}</b></div>", unsafe_allow_html=True)

                    st.markdown(f"<div class='hartim-box'><small style='color: #adb5bd;'>THE HARTIM EQUATION RESULT</small><h1 style='text-align: left; color: #ff4b4b; font-size: 80px;'>{h_score:.2f}</h1></div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if title not in st.session_state.watched_movies:
                        if st.button("✅ Bu Filmi İzledim Arşive Ekle", use_container_width=True):
                            st.session_state.watched_movies.append(title)
                            st.rerun()
                    else:
                        st.success(f"✅ {title} Korku Arşivinizde.")

                    tweet = f"🎬 {title} filminin Hartim Skoru: {h_score:.2f} 🔥\n\nGerçek janr terazisi ile sen de keşfet: [LINK_BURAYA]"
                    st.link_button("🚀 Sonucu X'te Paylaş", f"https://twitter.com/intent/tweet?text={tweet.replace(' ', '%20')}")
                
                st.session_state.current_movie_id = "" # İşlem bitince ID'yi temizle
            else:
                st.error("🛑 Bu uygulama sadece SAF KORKU filmleri içindir. Komedi, animasyon veya aile filmleri kabul edilmez.")
                st.session_state.current_movie_id = ""
        else:
            st.error("🛑 Sistem eşleşme sağlayamadı veya veri bulunamadı.")
    else:
        st.error("🛑 Film bulunamadı veya kriterlere uygun veri çekilemedi.")
