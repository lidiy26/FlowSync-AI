# 📋 Ürün Gereksinim Dokümanı (PRD): FlowSync AI
> **Sürüm:** 1.0.0 | **Kapsam:** Akıllı Şehir & Rota Optimizasyonu

## 1. Ürün Özeti & Vizyon
FlowSync AI, toplu taşımayı "sabit" bir yapıdan "canlı" bir organizmaya dönüştürür. Talep duyarlı (demand-responsive) mimarisi sayesinde hem belediyelerin filo verimliliğini maksimize eder hem de yolcuların konforunu (doluluk yönetimiyle) optimize eder.

## 2. Kullanıcı Grupları
* **Yolcu:** En hızlı değil, "en optimum" (boş ve hızlı) yolu seçen kişi.
* **Operatör (Belediye):** Filoyu anlık verilere göre yöneten, sefer sayılarını talebe göre güncelleyen karar verici.

## 3. Temel Özellikler (Key Features)
### 3.1. Dinamik Sefer & Rota Yönetimi (Admin)
- **Talep Duyarlı Planlama:** Yığılma olan duraklara (maç, konser, kaza) otomatik ek sefer veya rota kaydırma önerisi.
- **Esnek Durak Mantığı:** Mikro-transit araçlar için talebe göre dinamik durak noktaları belirleme.
### 3.2. Sistem Seviyesinde Yük Dengeleme (Nudging)
- **Kitle Yönlendirme:** Aşırı yoğun hatlardaki yolcuları, oyunlaştırma veya teşviklerle (puan/indirim) yan hatlara dağıtarak trafik tıkanıklığını oluşmadan önleme.
### 3.3. AI Tabanlı Doluluk & Talep Tahmini
- **Görüntü İşleme/Bilet Verisi:** Araç içindeki doluluğu duraktaki yolcuya canlı iletme.
- **Öngörücü Analiz:** Yarınki hava durumu veya etkinlik takvimine göre duraklardaki yolcu sayısını 1 saat önceden tahmin etme.
### 3.4. Hibrit Operasyon Paneli
- Belediyeler için "Komuta Kontrol Merkezi" (Anlık filo takibi, yakıt verimliliği, rota analizi).

## 4. Teknik Gereksinimler
- **Algoritmalar:** Graph Neural Networks (Şehir ağı analizi için) ve Reinforcement Learning (Rota optimizasyonu için).
- **Veri Kaynakları:** GTFS-Realtime verileri, GPS verileri ve anonimleştirilmiş mobil sinyaller.

## 5. Başarı Kriterleri (KPI)
- Duraklardaki bekleme sürelerinde %25 azalma.
- Araç doluluk oranlarının hat genelinde homojen dağılması (yığılmanın önlenmesi).
- Gereksiz seferlerin elimine edilmesiyle karbon emisyonunda %15 düşüş.

## 6. MVP / V1 / V2 Kapsam Yol Haritası
### MVP (Sürüm 1.0.0 - “En az ama çalışır”)
- Baseline rota arama: tahmini seyahat süresi + basit “konfor skoru” (beklenen kalabalık) ile 2-3 alternatif rota göster.
- Basit doluluk/yoğunluk tahmini: zaman-of-gün + etkinlik/hava için yer tutucu (mock) sinyallerle 1 saat öncesi kaba tahmin.
- Yolcu tarafı nudging: ana hat kalabalığı yüksekse alternatif öneri + kullanıcıya açıklama.
- Operatör dashboard: durak bazında yoğunluk tahmini (kırmızı/yeşil) ve “önerilen ek sefer” metni.
- Gemini entegrasyonu (opsiyonel): önerilerin neden üretildiğini kullanıcıya metin olarak açıklayan “AI açıklaması” (model çıktısı güvenli/yalnızca açıklama amaçlı).

### V1 (“Pilot operasyon”)
- Gerçek veri bağlama: GTFS-Realtime (sefer/konum), GPS (araç konum), durak/hat eşleştirme.
- ETL/feature üretimi: normalize edilmiş zaman hizalama, durak/hat eşleştirme ve eksik veri stratejisi.
- Model kalibrasyonu: hata metrikleri (MAE/RMSE) ve geri test (backtesting) raporu.
- Operatör onay akışı: öneriyi kabul/ret etme ve denetim izi (audit trail).

### V2 (“Akıllı optimizasyon”)
- GNN tabanlı şehir analizi (baseline yerine öğrenen temsil).
- RL tabanlı rota/sefer optimizasyonu (güvenlik limitleriyle).
- KPI raporlama genişletme: yığılma homojenliği ve karbon emisyonu hesaplama yaklaşımının netleştirilmesi.