import streamlit as st
import requests
import math

# --- API ANAHTARLARI ---
OMDB_API_KEY = "230D910E"
TMDB_API_KEY = "ffa196d9c44790c7864d5aa4a06ca623"

# Sayfa Yapılandırması
st.set_page_config(page_title="The Hartim Curve", page_icon="⚖️", layout="wide")

# Görsel Stil (Premium Dark Mode + Scrollbar Gizleme)
st.markdown("""
    <style>
    /* Arayüzdeki kaydırma çubuklarını tamamen gizliyoruz */
    ::-webkit-scrollbar { display: none; }
    html, body { -ms-overflow-style: none; scrollbar-width: none; }
    
    .main { background-color: #0b0d11; color: white; }
    h1 { color: #ff4b4b; text-align: center; font-weight: 900; letter-spacing: -2px; }
    .stTextInput > div > div > input { background-color: #1a1c23; color: white; border: 1px solid #3d4148; }
    .metric-card { background-color: #1a1c23; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #2d3139; }
    .hartim-box { background-color: #1a1c23; padding: 30px; border-radius: 20px; border-left: 10px solid #ff4b4b; margin-top: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

st.title("THE HARTIM CURVE")
st.markdown("<p style='text-align: center; color: #adb5bd;'>IMDb • Metacritic • Tomatometer • TMDb</p>", unsafe_allow_html=True)

movie_name = st.text_input("", placeholder="Analiz edilecek filmi yazın... (Örn: Errementari)")

if movie_name:
    # 1. Motor: OMDb (IMDb, Meta, RT)
    omdb_url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    o_data = requests.get(omdb_url).json()

    # 2. Motor: TMDb (TMDb User Score)
    tmdb_search = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    t_search_data = requests.get(tmdb_search).json()

    if o_data.get("Response") == "True" and t_search_data.get("results"):
        # Veri Toplama
        title = o_data.get("Title")
        poster = o_data.get("Poster")
        
        # Puanları Çıkarma (10'luk sistemde normalize etme)
        p_imdb = float(o_data.get("imdbRating", 0)) if o_data.get("imdbRating") != "N/A" else 0
        p_meta = int(o_data.get("Metascore")) / 10 if o_data.get("Metascore") != "N/A" else 0
        
        p_tomato = 0
        for r in o_data.get("Ratings", []):
            if r['Source'] == 'Rotten Tomatoes':
                p_tomato = int(r['Value'].replace('%', '')) / 10
        
        p_tmdb = t_search_data["results"][0].get("vote_average", 0)

        # Temel Ortalama (The 4 Pillars)
        active_scores = [p for p in [p_imdb, p_meta, p_tomato, p_tmdb] if p > 0]
        B = sum(active_scores) / len(active_scores) if active_scores else 0

        if B > 0:
            # --- THE HARTIM EQUATION (Gauss RBF Modeli) ---
            # Merkezi 6.75 olan çan eğrisi formülü
            bonus = 0.85 * math.exp(-((B - 6.75)**2) / (2 * 1.8**2))
            h_score = B + bonus
            h_score = min(h_score, 10.0) # Kesinlikle 10'u geçemez kuralı
            
            # Dinamik Etiketleme Mantığı
            if h_score < 5.0:
                label, color = "💀 ÇÖP (Kurtarılamaz)", "#6c757d"
            elif h_score < 6.5:
                label, color = "🕯️ ZAYIF IŞIK (İzlenebilir)", "#adb5bd"
            elif h_score < 7.5:
                label, color = "💎 GİZLİ CEVHER", "#ffd700"
            elif h_score < 8.5:
                label, color = "🔥 JANR ONUR LİSTESİ", "#ff4b4b"
            else:
                label, color = "🏆 ÖLÜMSÜZ EFSANE", "#ffffff"

            # Arayüz
            st.divider()
            col1, col2 = st.columns([1, 1.5])
            
            with col1:
                st.image(poster if poster != "N/A" else "https://via.placeholder.com/300x450")
            
            with col2:
                st.header(title)
                
                # Puan Tablosu
                m1, m2, m3, m4 = st.columns(4)
                m1.markdown(f"<div class='metric-card'><small>IMDb</small><br><b>{p_imdb if p_imdb>0 else '-'}</b></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-card'><small>Meta</small><br><b>{p_meta if p_meta>0 else '-'}</b></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-card'><small>Tomato</small><br><b>{p_tomato if p_tomato>0 else '-'}</b></div>", unsafe_allow_html=True)
                m4.markdown(f"<div class='metric-card'><small>TMDb</small><br><b>{p_tmdb if p_tmdb>0 else '-'}</b></div>", unsafe_allow_html=True)

                # Final Kutu
                st.markdown(f"""
                    <div class='hartim-box'>
                        <small style='color: #adb5bd;'>THE HARTIM EQUATION RESULT</small>
                        <h1 style='text-align: left; margin: 0; color: #ff4b4b; font-size: 80px;'>{h_score:.2f}</h1>
                        <p style='color: {color}; font-weight: bold; font-size: 20px;'>{label}</p>
                    </div>
                """, unsafe_allow_html=True)

                # Paylaş
                tweet = f"🎬 {title} filminin Hartim Skoru: {h_score:.2f} 🔥\n\n4 dev platformun ortalaması ve özel janr eğrisiyle gerçeği gör: [LINK_BURAYA]"
                st.link_button("🚀 Sonucu X'te Paylaş", f"https://twitter.com/intent/tweet?text={tweet.replace(' ', '%20')}")
        else:
            st.warning("Bu film için yeterli puan verisi bulunamadı.")
    else:
        st.error("Film bulunamadı. Lütfen İngilizce adını yazmayı veya harf hatası yapmadığınızı kontrol edin.")
