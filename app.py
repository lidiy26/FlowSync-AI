import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. SİSTEM YAPILANDIRMASI & VERİ MERKEZİ ---
st.set_page_config(page_title="FlowSync AI | Global Command Center", page_icon="🌐", layout="wide")

# PRD 4.0: Dinamik Veri Kaynakları (Mock)
CITY_DATA = {
    "İstanbul": {
        "Duraklar": ["Kadıköy", "Beşiktaş", "Zincirlikuyu", "Üsküdar"],
        "Koordinat": [41.0082, 28.9784],
        "Hatlar": {
            "Kadıköy": ["15F - Beykoz", "14R - Rasathane", "11T - Türkiş"],
            "Beşiktaş": ["28T - Topkapı", "30M - Mecidiyeköy", "129T - Bostancı"],
            "Zincirlikuyu": ["500T - Tuzla", "34G - Metrobüs", "25G - Sarıyer"],
            "Üsküdar": ["11ÜS - Sultanbeyli", "15P - Soğuksu", "12H - Kadıköy"]
        }
    },
    "Ankara": {
        "Duraklar": ["Kızılay", "AŞTİ", "Ulus", "Çayyolu"],
        "Koordinat": [39.9334, 32.8597],
        "Hatlar": {
            "Kızılay": ["114 - Kırkkonaklar", "185 - Oran", "413 - Altınpark"],
            "AŞTİ": ["442 - Havalimanı", "104 - Gölbaşı", "158 - Haymana"],
            "Ulus": ["203 - İncirli", "312 - Karapürçek", "440 - Pursaklar"],
            "Çayyolu": ["511 - Sincan", "584 - Bilkent", "590 - Yaşamkent"]
        }
    },
    "İzmir": {
        "Duraklar": ["Konak", "Alsancak", "Bornova", "Karşıyaka"],
        "Koordinat": [38.4237, 27.1428],
        "Hatlar": {
            "Konak": ["10 - Gümrük", "253 - Halkapınar", "951 - Montrö"],
            "Alsancak": ["912 - Egekent", "921 - Bostanlı", "963 - Evka-3"],
            "Bornova": ["59 - Yerel", "800 - Menemen", "268 - Doğanlar"],
            "Karşıyaka": ["121 - Mavişehir", "777 - Doğal Yaşam", "126 - Cumhuriyet"]
        }
    }
}

# --- 2. YARDIMCI MÜHENDİSLİK FONKSİYONLARI ---
def simulate_fleet_status():
    """Hat doluluklarını ve gecikmeleri anlık simüle eder."""
    status = random.choice(["🟢 Stabil", "🟡 Yoğun", "🔴 Kritik"])
    return status

# --- 3. ANA ARAYÜZ ---
st.title("🌐 FlowSync AI: Akıllı Şehir Mobilite Ekosistemi")
st.markdown(f"**Sürüm:** 1.6.0 | **Mod:** {'Üretim (Simüle)'} | **Tarih:** {time.strftime('%Y-%m-%d')}")

# Sekme Yapısı (PRD 3.0 & 6.0 Kapsamı)
tab1, tab2, tab3 = st.tabs(["📱 Yolcu Planlayıcı", "🎮 Operatör Komuta Merkezi", "📊 Verimlilik & KPI"])

# --- TAB 1: YOLCU PLANLAYICI (GELİŞMİŞ NUDGING) ---
with tab1:
    col_input, col_output = st.columns([1, 2])

    with col_input:
        st.subheader("📍 Seyahat Planla")
        secilen_il = st.selectbox("Şehir Seçiniz:", list(CITY_DATA.keys()))
        duraklar = CITY_DATA[secilen_il]["Duraklar"]
        secilen_durak = st.selectbox("Mevcut Durağınız:", duraklar)
        hedef = st.text_input("Hedef Noktası:", "Merkez / İş")

        st.write("---")
        oncelik = st.radio("Sizin İçin Hangisi Önemli?", ["En Hızlı ⚡", "En Konforlu 🍃", "En Çok Puan 💰"])

    with col_output:
        st.subheader(f"✨ {secilen_durak} Durağı Canlı Rota Önerileri")
        uygun_hatlar = CITY_DATA[secilen_il]["Hatlar"][secilen_durak]

        for hat in uygun_hatlar:
            # PRD 3.3: Doluluk Tahmini Simülasyonu
            doluluk = np.random.randint(15, 95)
            bekleme = np.random.randint(2, 18)

            # Dinamik Renklendirme
            if doluluk > 80: color, status = "red", "🔴 Tıklım Tıklım"
            elif doluluk > 45: color, status = "orange", "🟡 Dolu"
            else: color, status = "green", "🟢 Boş & Konforlu"

            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"#### 🚌 {hat}")
                c1.write(f"**Durum:** {status} (%{doluluk}) | **Varış:** {bekleme} dk")

                # PRD 3.2: Nudging (Yönlendirme)
                if doluluk > 60:
                    c1.warning("💡 Bu hat yoğun. 10 dk sonraki sefer %30 daha boş görünüyor.")

                if c2.button("Seç", key=f"select_{hat}"):
                    st.success(f"Rota Onaylandı! 15 'Eco-Point' kazandınız. 🌱")
                    st.balloons()

# --- TAB 2: OPERATÖR KOMUTA MERKEZİ (KRİTİK MÜDAHALE) ---
with tab2:
    st.subheader(f"🎮 {secilen_il} Saha Yönetim Paneli")

    # 1. KPI Metrikleri
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Aktif Otobüs", f"{np.random.randint(100, 150)}", "+5")
    m2.metric("Ort. Bekleme", f"{np.random.randint(4, 8)} dk", "-1.2 dk")
    m3.metric("Müşteri Skoru", "4.8/5", "+0.2")
    m4.metric("CO2 Tasarrufu", "1450 kg", "+120 kg")

    st.divider()

    # 2. Kritik Hat Uyarıları & Müdahale (PRD 3.1)
    col_alerts, col_map = st.columns([1, 2])

    with col_alerts:
        st.error("⚠️ KRİTİK YOĞUNLUK TESPİT EDİLDİ")
        st.write("**Hat:** 500T - Zincirlikuyu Yönü")
        st.write("**Doluluk:** %94")
        if st.button("🚀 YEDEK OTOBÜS SEVK ET", use_container_width=True):
            st.toast("Yedek araç depodan çıkış yaptı!", icon="🚌")

        st.divider()
        st.warning("⚡ SEFER SIKLAŞTIRMA ÖNERİSİ")
        st.write("**Bölge:** Kızılay / Ankara")
        if st.button("Onayla (2 dk Aralık)", use_container_width=True):
            st.info("Sinyalizasyon güncellendi.")

    with col_map:
        st.write("**Canlı Filo İzleme (GPS)**")
        center_lat = CITY_DATA[secilen_il]["Koordinat"][0]
        center_lon = CITY_DATA[secilen_il]["Koordinat"][1]
        map_points = pd.DataFrame(
            np.random.randn(30, 2) / [70, 70] + [center_lat, center_lon],
            columns=['lat', 'lon']
        )
        st.map(map_points)

# --- TAB 3: VERİMLİLİK & KPI ANALİTİĞİ ---
with tab3:
    st.subheader("📈 Mühendislik Analiz Raporu")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.write("**Günlük Doluluk Oranı Değişimi**")
        st.line_chart(np.random.randn(20, 1) + 50)

    with col_chart2:
        st.write("**Yakıt Verimliliği vs. Yolcu Sayısı**")
        st.area_chart(np.random.randn(20, 2))

    st.divider()
    st.markdown("""
    ### 📑 PRD Hedef Takibi (V1.0)
    - [x] **Dinamik Rota Yönetimi:** Başarılı (Simüle veri ile).
    - [x] **Yolcu Nudging:** Aktif (Puanlama ve alternatif rota önerisi).
    - [x] **Operatör Dashboard:** Aktif (Müdahale butonları ve harita).
    - [ ] **Gerçek Veri Entegrasyonu:** (V2 Pilot aşamasında planlanıyor).
    """)

# --- SIDEBAR (SİSTEM AYARLARI) ---
st.sidebar.image("https://img.icons8.com/clouds/100/000000/bus.png")
st.sidebar.header("Sistem Ayarları")
st.sidebar.selectbox("Dil / Language:", ["Türkçe", "English"])
if st.sidebar.button("Sistem Loglarını İndir"):
    st.sidebar.write("Log dosyası hazır: `flowsync_log_v1.csv`")
