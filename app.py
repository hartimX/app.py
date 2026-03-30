import streamlit as st

# Sayfa Tasarımı
st.set_page_config(page_title="Korku Terazisi", page_icon="🕯️", layout="centered")

# Görsel Stil (CSS ile Karanlık Tema)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #e63946; }
    h1 { color: #e63946; text-align: center; font-family: 'Courier New', Courier, monospace; }
    .stNumberInput label { color: #f1faee !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🕯️ KORKU TERAZİSİ")
st.subheader("Genel izleyiciye değil, janrın ruhuna güven.")

# Girdiler
col1, col2 = st.columns(2)
with col1:
    imdb = st.number_input("IMDb Puanı", 0.0, 10.0, 6.4, step=0.1)
with col2:
    meta = st.number_input("Metascore (0-100)", 0, 100, 80, step=1)

# Parabolik H-Score Hesaplama
B = (2 * imdb + (meta / 10)) / 3
h_score = B + (B * (10 - B) / 25)

# Sonuç Ekranı
st.divider()
st.markdown(f"<h2 style='text-align: center; color: white;'>H-Score: {h_score:.2f}</h2>", unsafe_allow_html=True)

# Durum Analizi
if h_score >= 8.5:
    st.error("🏆 BİR BAŞYAPIT: Bu filmi izlememek janra ihanettir.")
elif h_score >= 7.0:
    st.warning("🔥 GİZLİ CEVHER: 7'lik korku aslında çok iyidir. Mutlaka bak!")
else:
    st.info("💀 SIRADAN: Janr severler için bile ortalama bir deneyim.")

# X Paylaşım Butonu
tweet_text = f"İzlediğim korku filminin gerçek puanını buldum! 🎬\n\nIMDb: {imdb}\nH-Score: {h_score:.2f} 🔥\n\nSenin cevherin hangisi? Buradan hesapla: [LİNKİ_BURAYA_EKLE]"
tweet_url = f"https://twitter.com/intent/tweet?text={tweet_text.replace(' ', '%20').replace('\n', '%0A')}"
st.link_button("🚀 Sonucu X'te Paylaş", tweet_url)
