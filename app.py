import streamlit as st
import requests
import math
import random

# --- API ANAHTARLARI ---
OMDB_API_KEY = "230D910E"
TMDB_API_KEY = "ffa196d9c44790c7864d5aa4a06ca623"

# Sayfa Yapılandırması
st.set_page_config(page_title="The Hartim Curve", page_icon="⚖️", layout="wide")

# --- HAFIZA YÖNETİMİ (Session State) ---
if 'watched_movies' not in st.session_state:
    st.session_state.watched_movies = []
if 'current_movie' not in st.session_state:
    st.session_state.current_movie = ""
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

def get_random_horror():
    # TMDb'den (Genre: 27) rastgele popüler bir korku filmi sayfası çekiyoruz
    page = random.randint(1, 20)
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres=27&page={page}"
    res = requests.get(url).json()
    if res.get("results"):
        movies = [m['title'] for m in res['results']]
        # Kara liste filtresi devredeyse izlenenleri eliyoruz
        if st.session_state.get('filter_watched', True):
            movies = [m for m in movies if m not in st.session_state.watched_movies]
        
        if movies:
            st.session_state.current_movie = random.choice(movies)
            st.session_state.search_query = st.session_state.current_movie

def update_search():
    st.session_state.current_movie = st.session_state.search_query

# Görsel Stil (Premium Kırmızı-Siyah Tema + Okunabilirlik + Kaydırma Çubuğu Gizleme)
st.markdown("""
    <style>
    ::-webkit-scrollbar { display: none; }
    html, body { -ms-overflow-style: none; scrollbar-width: none; background-color: #000000; }
    
    .main { background-color: #000000; color: white; }
    
    h1 { color: #ff0000; text-align: center; font-weight: 900; letter-spacing: -2px; margin-bottom: 0px; }
    .slogan { text-align: center; color: #adb5bd; font-size: 1.1rem; margin-top: 5px; margin-bottom: 20px; }

    .stTextInput input {
        color: #ffffff !important; 
        background-color: #1a1c23;
        border: 2px solid #ff0000; 
        border-radius: 5px;
        padding: 10px;
    }
    .stTextInput input::placeholder { color: #adb5bd !important; opacity: 0.8; }
    
    .metric-card {
        background-color: #1a1c23; padding: 15px; border-radius: 10px;
        text-align: center; border: 1px solid #2d3139; color: #ffffff; 
    }
    .metric-card small { color: #adb5bd; } 
    
    .hartim-box { 
        background-color: #1a1c23; padding: 30px; border-radius: 20px; 
        border-left: 10px solid #ff4b4b; margin-top: 20px; 
        box-shadow: 0 10px 30px rgba(255,0,0,0.2); 
    }
    
    .share-button { text-align: center; margin-top: 10px; }
    
    .opening-screen { text-align: center; margin-top: 100px; padding: 20px; }
    .opening-icon { font-size: 5rem; color: #ff0000; margin-bottom: 20px; }
    .opening-text { color: #adb5bd; font-size: 1.2rem; }
    
    /* Sidebar Stilleri */
    [data-testid="stSidebar"] { background-color: #0b0d11; border-right: 1px solid #2d3139; }
    </style>
    """, unsafe_allow_html=True)

# --- YAN MENÜ (Korku Arşivi) ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff0000;'>🎬 Korku Arşivi</h2>", unsafe_allow_html=True)
    st.checkbox("İzlediklerimi Önerme", value=True, key="filter_watched")
    st.divider()
    st.markdown("<h4 style='color: #adb5bd;'>İzlediklerim</h4>", unsafe_allow_html=True)
    if not st.session_state.watched_movies:
        st.markdown("<small style='color: #6c757d;'>Henüz film izlemediniz.</small>", unsafe_allow_html=True)
    else:
        for m in reversed(st.session_state.watched_movies):
            st.markdown(f"- <small style='color: #ffffff;'>{m}</small>", unsafe_allow_html=True)

# Ana Başlık
st.title("THE HARTIM CURVE")
st.markdown("<p class='slogan'>Gizli Korku Cevherlerini Keşfet</p>", unsafe_allow_html=True)

# Arama ve Öneri Barı (Yan Yana)
col_search, col_btn = st.columns([4, 1.2])
with col_search:
    st.text_input("", placeholder="Analiz edilecek korku filmini İNGİLİZCE yazın...", key="search_query", on_change=update_search)
with col_btn:
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.button("Bana Korku Öner 🎲", use_container_width=True, on_click=get_random_horror)

movie_name = st.session_state.current_movie

# Film Girilmediğinde (Açılış Ekranı)
if not movie_name:
    st.markdown("""
        <div class='opening-screen'>
            <div class='opening-icon'>🕯️</div>
            <p class='opening-text'>Korku Sinemasının Gerçek Terazisi seni bekliyor.</p>
            <p class='opening-text'>Arama yap veya zar atarak rastgele bir film keşfet.</p>
        </div>
    """, unsafe_allow_html=True)

# Film Aranmış veya Önerilmişse
elif movie_name:
    omdb_url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    o_data = requests.get(omdb_url).json()

    tmdb_search = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    t_search_data = requests.get(tmdb_search).json()

    if o_data.get("Response") == "True" and t_search_data.get("results"):
        
        # --- KAPI GÜVENLİĞİ: Sadece Korku Filmi Filtresi ---
        genre = o_data.get("Genre", "")
        if "Horror" not in genre:
            st.error("🛑 Uyarı: The Hartim Curve sadece korku janrı için tasarlanmış özel bir algoritmadır. Lütfen bir korku filmi girin veya 'Öner' butonunu kullanın.")
        else:
            title = o_data.get("Title")
            poster = o_data.get("Poster")
            
            p_imdb = float(o_data.get("imdbRating", 0)) if o_data.get("imdbRating") != "N/A" else 0
            p_meta = int(o_data.get("Metascore")) / 10 if o_data.get("Metascore") != "N/A" else 0
            
            p_tomato = 0
            for r in o_data.get("Ratings", []):
                if r['Source'] == 'Rotten Tomatoes':
                    p_tomato = int(r['Value'].replace('%', '')) / 10
            
            p_tmdb = t_search_data["results"][0].get("vote_average", 0)

            # --- AYRIŞMA PROTOKOLÜ (Divergence Shield) ---
            aud_scores = [p for p in [p_imdb, p_tmdb] if p > 0]
            crit_scores = [p for p in [p_meta, p_tomato] if p > 0]

            H = sum(aud_scores) / len(aud_scores) if aud_scores else 0
            E = sum(crit_scores) / len(crit_scores) if crit_scores else 0

            B = 0
            if H > 0 and E > 0:
                fark = H - E
                if fark >= 2.5: B = (H * 0.90) + (E * 0.10)
                elif fark >= 1.5: B = (H * 0.75) + (E * 0.25)
                else: B = (H * 0.50) + (E * 0.50)
            elif H > 0: B = H
            elif E > 0: B = E

            if B > 0:
                # --- THE HARTIM EQUATION ---
                bonus = 0.85 * math.exp(-((B - 6.75)**2) / (2 * 1.8**2))
                h_score = min(B + bonus, 10.0) 
                
                if h_score < 5.0: label, color = "💀 ÇÖP (Kurtarılamaz)", "#6c757d"
                elif h_score < 6.5: label, color = "🕯️ ZAYIF IŞIK (İzlenebilir)", "#adb5bd"
                elif h_score < 7.5: label, color = "💎 GİZLİ CEVHER", "#ffd700"
                elif h_score < 8.5: label, color = "🔥 JANR ONUR LİSTESİ", "#ff4b4b"
                else: label, color = "🏆 ÖLÜMSÜZ EFSANE", "#ffffff"

                # Arayüz
                st.divider()
                col1, col2 = st.columns([1, 1.5])
                
                with col1:
                    st.image(poster if poster != "N/A" else "https://via.placeholder.com/300x450")
                
                with col2:
                    st.header(title)
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.markdown(f"<div class='metric-card'><small>IMDb</small><br><b>{p_imdb if p_imdb>0 else '-'}</b></div>", unsafe_allow_html=True)
                    m2.markdown(f"<div class='metric-card'><small>Meta</small><br><b>{p_meta if p_meta>0 else '-'}</b></div>", unsafe_allow_html=True)
                    m3.markdown(f"<div class='metric-card'><small>Tomato</small><br><b>{p_tomato if p_tomato>0 else '-'}</b></div>", unsafe_allow_html=True)
                    m4.markdown(f"<div class='metric-card'><small>TMDb</small><br><b>{p_tmdb if p_tmdb>0 else '-'}</b></div>", unsafe_allow_html=True)

                    st.markdown(f"""
                        <div class='hartim-box'>
                            <small style='color: #adb5bd;'>THE HARTIM EQUATION RESULT</small>
                            <h1 style='text-align: left; margin: 0; color: #ff4b4b; font-size: 80px;'>{h_score:.2f}</h1>
                            <p style='color: {color}; font-weight: bold; font-size: 20px;'>{label}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # --- HAFIZA: İzledim Butonu ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    if title not in st.session_state.watched_movies:
                        if st.button("✅ Bu Filmi İzledim Arşive Ekle", use_container_width=True):
                            st.session_state.watched_movies.append(title)
                            st.rerun()
                    else:
                        st.success("✅ Bu filmi izlediniz ve Korku Arşivinize eklendi.")

                    # Paylaş
                    st.markdown("<div class='share-button'>", unsafe_allow_html=True)
                    tweet = f"🎬 {title} filminin Hartim Skoru: {h_score:.2f} 🔥\n\n4 dev platformun ortalaması ve özel janr eğrisiyle gerçeği gör: [LINK_BURAYA]"
                    st.link_button("🚀 Sonucu X'te Paylaş", f"https://twitter.com/intent/tweet?text={tweet.replace(' ', '%20')}")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Bu film için yeterli puan verisi bulunamadı.")
    else:
        st.error("Film bulunamadı. Lütfen İngilizce adını yazmayı veya harf hatası yapmadığınızı kontrol edin.")
