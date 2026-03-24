# FlowSync AI 
🌐 FlowSync AI: Akıllı Şehir Ulaşım ve Kapasite Yönetimi
📌 Problem Tanımı (The Problem)
Günümüz metropollerinde toplu taşıma sistemleri, dinamik talep değişimlerine statik sefer planlarıyla karşılık vermeye çalışmaktadır. Bu durum iki temel verimsizliğe yol açar:

Darboğazlar (Bottlenecks): Belirli hatlarda kapasitenin %100 üzerine çıkılması sonucu yolcu konforunun düşmesi ve duraklarda aşırı bekleme süreleri.

Atıl Kapasite: Bazı hatların çok düşük dolulukla çalışması sonucu kaynak (yakıt, personel, zaman) israfı ve yüksek karbon emisyonu.

Kullanıcıların (yolcuların) sistemdeki anlık yoğunluktan haberdar olmaması, talebin dengesiz dağılmasına neden olan temel "bilgi asimetrisi" sorunudur.

🚀 Çözüm: FlowSync AI (The Solution)
FlowSync AI, Endüstri Mühendisliği'nin Kapasite Planlama ve Nudging (Dürtme) teorilerini kullanarak bu sorunu çift taraflı çözer:

Yolcu Odaklı Optimizasyon: Yolculara sadece rota değil, "Konfor Skoru" ve "Karbon Tasarrufu" verilerini sunarak, talebi yoğun saatlerden veya hatlardan daha boş olanlara kaydırır.

Operatör Karar Destek Sistemi: Operasyon merkezine canlı "Kritik Yoğunluk" uyarıları göndererek, insana dayalı hata payını azaltır ve Tam Zamanında (Just-in-Time) yedek araç sevkiyatı sağlar.

✨ Temel Özellikler
Multi-City Hub: İstanbul, Ankara ve İzmir şehirleri için özelleştirilmiş durak ve hat simülasyonu.

Akıllı Nudging Sistemi: Yolcuları daha sürdürülebilir ve konforlu seçimler yapmaya teşvik eden ödül mekanizması.

Canlı Operatör Paneli: Tek tıkla filo müdahalesi ve kapasite artırımı.

Mühendislik Metrikleri: Doluluk oranı, bekleme süresi, konfor skoru ve CO2 tasarrufu takibi.

🛠️ Teknik Altyapı
Dil: HTML5, CSS3 (Tailwind CSS), JavaScript (ES6+)

Mantık: Dinamik Veri Yapıları (JSON tabanlı simülasyon)

Yayın: Netlify (CI/CD entegrasyonu ile GitHub üzerinden otomatik deployment)

🔗 Canlı Uygulama
Projeyi canlı incelemek için: [https://69c29b8f6aa6bb0f8b62f355--fancy-nasturtium-fdc9b5.netlify.app/]                        [http://localhost:8501/]   
]http://localhost:8501/
Bu proje, PRD kapsamına göre `MVP` seviyesinde çalışan bir Streamlit arayüzü sağlar:
- Yolcu için rota arama ve “konfor skoru”
- Yoğunluk yüksekse nudging (alternatif önerisi)
- Operatör için durak bazında yoğunluk (kırmızı/yeşil) ve önerilen ek sefer
- İsteğe bağlı Gemini tabanlı “AI açıklaması”

Varsayılan olarak mock (örnek) veri kullanılır. GTFS-Realtime/GPS ingest bağlandığında gerçek verilere geçilebilir.


## Kurulum

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r 
```

Alternatif: PowerShell ortam değişkeni olarak `GOOGLE_API_KEY` tanımlayabilirsiniz.

## Çalıştırma

```powershell
streamlit run app.py
```

