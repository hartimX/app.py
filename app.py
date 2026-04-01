import streamlit as st
import requests
import math
import random
from datetime import datetime

# --- API ANAHTARLARI ---
OMDB_API_KEY = "230D910E"
TMDB_API_KEY = "ffa196d9c44790c7864d5aa4a06ca623"


# Sayfa Yapılandırması (kapak görseli)
st.set_page_config(
    page_title="The Hartim Curve | Gerçek Korku Terazisi", 
    page_icon="⚖️", 
    layout="wide",
    menu_items={
        'Get Help': 'https://twitter.com/senin_twitter_hesabin',
        'About': "The Hartim Curve: Gizli Korku Cevherlerini Keşfet"
    }
)

# Streamlit için meta etiketleri eklemek (X Önizlemesi İçin)
st.markdown(f"""
    <head>
        <meta property="og:title" content="The Hartim Curve | Gerçek Korku Terazisi" />
        <meta property="og:description" content="Gizli Korku Cevherlerini Keşfet. Kendi korku zevkini test et!" />
        <meta property="og:image" content="https://github.com/hartimX/app.py/blob/main/12.jpg?raw=true" />
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:title" content="The Hartim Curve | Gerçek Korku Terazisi" />
        <meta property="twitter:description" content="Gizli Korku Cevherlerini Keşfet. Kendi korku zevkini test et!" />
        <meta property="twitter:image" content="https://github.com/hartimX/app.py/blob/main/12.jpg?raw=true" />
    </head>
""", unsafe_allow_html=True)

# --- HAFIZA YÖNETİMİ ---
if 'watched_movies' not in st.session_state: st.session_state.watched_movies = []
if 'current_movie_id' not in st.session_state: st.session_state.current_movie_id = ""
if 'search_query' not in st.session_state: st.session_state.search_query = ""

def get_random_horror():
    # Arka planda 1000 oy barajını geçene kadar sessizce zar atar (Maksimum 5 sayfa dener)
    for _ in range(5):
        page = random.randint(1, 25)
        # Komedi (35) yasağı kaldırıldı! Korku-Komediler artık serbest.
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres=27&without_genres=16,10751&vote_count.gte=50&page={page}"
        res = requests.get(url).json()
        
        if res.get("results"):
            movies = [m for m in res['results'] if m['title'] not in st.session_state.watched_movies]
            random.shuffle(movies) # Rastgeleliği artırmak için karıştır
            
            for chosen in movies:
                tmdb_id = chosen.get("id")
                # OMDb baraj kontrolünü sana göstermeden arka planda yap
                detail = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}").json()
                imdb_id = detail.get("imdb_id")
                
                if imdb_id:
                    o_data = requests.get(f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}").json()
                    if o_data.get("Response") == "True":
                        try:
                            imdb_votes = int(o_data.get("imdbVotes", "0").replace(",", ""))
                        except:
                            imdb_votes = 0
                        
                        # Eğer 1000 oyu geçiyorsa ekrana basmak üzere hafızaya al ve döngüyü bitir!
                        if imdb_votes >= 1000:
                            st.session_state.current_movie_id = tmdb_id
                            st.session_state.search_query = chosen.get("title")
                            return

# Görsel Stil
st.markdown("""
    <style>
    ::-webkit-scrollbar { display: none; }
    html, body { -ms-overflow-style: none; scrollbar-width: none; background-color: #000000; }
    .main { background-color: #000000; color: white; }
    h1 { color: #ff0000; text-align: center; font-weight: 900; letter-spacing: -2px; margin-bottom: 0px; }
    .slogan { text-align: center; color: #adb5bd; font-size: 1.1rem; margin-top: 5px; margin-bottom: 20px; }
    .stTextInput input { color: #ffffff !important; background-color: #1a1c23 !important; -webkit-text-fill-color: #ffffff !important; border: 2px solid #ff0000; border-radius: 5px; padding: 10px; }
    .stTextInput input::placeholder { color: #adb5bd !important; -webkit-text-fill-color: #adb5bd !important; opacity: 0.8 !important; }
    .metric-card { background-color: #1a1c23; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #2d3139; color: #ffffff; }
    .metric-card small { color: #adb5bd; }
    .metric-card a { color: #ffffff; text-decoration: none; border-bottom: 1px dashed #adb5bd; }
    .metric-card a:hover { color: #ff4b4b; border-bottom: 1px solid #ff4b4b; }
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
    st.text_input("", placeholder="Korku filmini ingilizce yazın...", key="search_query")
with col_btn:
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.button("Bana Korku Öner 🎲", use_container_width=True, on_click=get_random_horror)

target = st.session_state.search_query
if not target:
    st.markdown("""<div class='opening-screen'><div class='opening-icon'>🕯️</div><p style='color: #adb5bd;'>Korku Sinemasının Gerçek Terazisi seni bekliyor.</p></div>""", unsafe_allow_html=True)
else:
    movie_id = ""
    p_tmdb = 0
    is_pure_horror = False

    # --- TMDb: TEK TÜR OTORİTESİ ---
    if st.session_state.current_movie_id:
        tmdb_url = f"https://api.themoviedb.org/3/movie/{st.session_state.current_movie_id}?api_key={TMDB_API_KEY}"
        t_res = requests.get(tmdb_url).json()
        if t_res.get("vote_count", 0) >= 50:
            movie_id = t_res.get("imdb_id")
            p_tmdb = t_res.get("vote_average", 0)
            is_pure_horror = True

    else:
        tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={target}"
        t_search = requests.get(tmdb_url).json()
        
        if t_search.get("results"):
            valid_results = sorted(t_search['results'], key=lambda x: x.get('vote_count', 0), reverse=True)
            for candidate in valid_results[:5]:
                detail = requests.get(f"https://api.themoviedb.org/3/movie/{candidate['id']}?api_key={TMDB_API_KEY}").json()
                genre_names = [g['name'] for g in detail.get('genres', [])]
                
                # SAF KORKU (Komedi artık dışlanmıyor)
                if "Horror" in genre_names and not any(bad in genre_names for bad in ["Animation", "Family"]):
                    
                    if detail.get("vote_count", 0) >= 30:
                        movie_id = detail.get('imdb_id')
                        p_tmdb = detail.get("vote_average", 0)
                        is_pure_horror = True
                        break

    if is_pure_horror and movie_id:
        o_data = requests.get(f"http://www.omdbapi.com/?i={movie_id}&apikey={OMDB_API_KEY}").json()
        
        if o_data.get("Response") == "True":
            
            # --- IMDb 1000 OY BARAJI (Eş-Dost Koruması) ---
            imdb_votes_str = o_data.get("imdbVotes", "0").replace(",", "")
            try:
                imdb_votes = int(imdb_votes_str)
            except:
                imdb_votes = 0
                
            if imdb_votes < 1000:
                st.info(f"🛑 Güvenlik Barajı: Bu film IMDb'de 1000 oy barajını geçemediği için (Oy: {imdb_votes}) The Hartim Curve tarafından reddedildi.")
                st.session_state.current_movie_id = ""
                st.stop()
            
            title = o_data.get("Title")
            poster = o_data.get("Poster")

            # Rotten Tomatoes İptal
            p_imdb = float(o_data.get("imdbRating", 0)) if o_data.get("imdbRating") != "N/A" else 0
            p_meta = int(o_data.get("Metascore")) / 10 if o_data.get("Metascore") != "N/A" else 0

            # --- SEYİRCİ VE ELEŞTİRMEN TERAZİSİ (v5.2) ---
            H = (p_imdb + p_tmdb) / 2 if (p_imdb > 0 and p_tmdb > 0) else (p_imdb or p_tmdb)
            E = p_meta

            if H > 0 or E > 0:
                if H > 0 and E > 0:
                    if H - E >= 1.5:
                        # Korku Severin Kalkanı: Seyirci sevdi, eleştirmen gömdü
                        B = (H * 0.90) + (E * 0.10)
                    elif E - H >= 1.5:
                        # Anti-Snob Freni: Eleştirmen sevdi, seyirci gömdü
                        B = (H * 0.80) + (E * 0.20)
                    else:
                        # Diplomatik: Doğal Salınım
                        B = (H * 0.50) + (E * 0.50)
                else: 
                    B = H or E

                # --- THE HARTIM EQUATION ---
                h_score = min(B + (0.85 * math.exp(-((B - 6.75)**2) / (2 * 1.8**2))), 10.0)
                
                # --- UI İÇİN GÜVENLİ PUAN FORMATLAMASI ---
                if p_imdb > 0:
                    imdb_str = f"<a href='https://www.imdb.com/title/{movie_id}/' target='_blank' title='IMDb Sayfasına Git'><b>{p_imdb} <span style='font-size: 0.8em;'>↗</span></b></a>"
                else:
                    imdb_str = "<b>-</b>"
                    
                meta_str = f"<b>{p_meta}</b>" if p_meta > 0 else "<b>-</b>"
                tmdb_str = f"<b>{p_tmdb:.1f}</b>" if p_tmdb > 0 else "<b>-</b>"

                # --- ARAYÜZ ÇİZİMİ ---
                st.divider()
                c1, c2 = st.columns([1, 1.5])
                with c1: st.image(poster if poster != "N/A" else "https://via.placeholder.com/300x450")
                with c2:
                    st.header(title)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.markdown(f"<div class='metric-card'><small>IMDb</small><br>{imdb_str}</div>", unsafe_allow_html=True)
                    m2.markdown(f"<div class='metric-card'><small>Meta</small><br>{meta_str}</div>", unsafe_allow_html=True)
                    m3.markdown(f"<div class='metric-card'><small>TMDb</small><br>{tmdb_str}</div>", unsafe_allow_html=True)

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
                
                st.session_state.current_movie_id = ""
            else:
                st.info("🛑 Bu film için hesaplama yapılabilecek hiçbir platform puanı bulunamadı.")
                st.session_state.current_movie_id = ""
        else:
            st.info("🛑 Film verileri çekilirken bir hata oluştu.")
            st.session_state.current_movie_id = ""
    else:
        st.info("🛑 The Hartim Curve güvenlik barajları: Bu film yeterli oy sayısına ulaşamamış veya animasyon/aile filmi kategorisine girmiş olabilir.")
        st.session_state.current_movie_id = ""
