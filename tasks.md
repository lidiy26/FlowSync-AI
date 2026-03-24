# FlowSync AI - Görev Listesi

Dayanak: `PRD.md` (Sürüm 1.0.0)

Not: Bu liste, uygulamayı adım adım geliştirmek için başlangıç planıdır. Proje ilerledikçe veri kaynakları, mimari ve teknik tercihler netleştikçe görevler parçalanabilir/yeniden sıralanabilir.

---

## 1. Temel tasarım ve kapsam netleştirme
- [x] PRD’yi MVP / V1 / V2 şeklinde parçala (hangi KPI’lar hangi sürümde hedeflenecek)
- [x] Hedef kullanıcı akışlarını çıkar (Yolcu seçimi, Operatör panel operasyonu)
- [x] Veri sözlüğü oluştur (GTFS-Realtime, GPS, anonim mobil sinyaller, bilet/görüntü verisi)
- [x] Gizlilik ve anonimleştirme gereksinimlerini yaz (veri saklama, maskeleme, erişim)
- [x] Sistem mimarisini belirle (veri akışı + model servisi + karar/optimizasyon + panel)

## 2. Veri toplama ve ingest altyapısı (Data Pipeline)
- [x] GTFS-Realtime tüketimi için ingest modülü kur (sefer/rota/konum event’leri) (mock)
- [x] GPS verisi ingest akışı tasarla (araç konum güncellemeleri zaman serisi) (mock)
- [x] Anonim mobil sinyal ingest akışı tasarla (durak bazlı/zon bazlı sinyale çeviri) (mock)
- [x] Veriyi normalize et (zaman hizalama, durak/hat eşleştirme, eksik değer stratejisi) (mock normalize)
- [x] Ham veriden “model için özellik” (feature) üretimine giden ETL şemasını tanımla (mock ETL)

## 3. Şehir ağı (Graph) ve rota/hat temsilinin temeli
- [x] Şehir ağını Graph formatında kur (durak/nodes, bağlantılar/edges)
- [x] Edge/node feature setini çıkar (seyahat süreleri, kapasite/hat yoğunluğu, etkinlik sinyali vb.)
- [x] Baseline rota çıkarımını uygula (kısa yol yerine “optimum” için başlangıç heuristic)
- [x] Simülasyon için zaman adımlı veri yapısını oluştur (timestamp -> graph state)

## 4. AI Tabanlı doluluk tahmini (Occupancy Estimation)
- [x] Veri kaynağı seçimini yap (MVP: demo/heuristic + regresyon; V1’de bilet/görüntü/hibrid bağlanacak)
- [x] Doluluk etiketleme yaklaşımını belirle (target: durak için `Beklenen Doluluk (%)`)
- [x] Baseline doluluk tahmin modeli (ör. regresyon) kur (lineer regresyon baseline)
- [x] İleri model seç ve prototiple (MVP: regression baseline; V1’de bilet/görüntü/hibrid bağlanacak)
- [x] Doluluk tahmin çıktısını durak/hat bazında zaman serisine dönüştür (time series üretimi)
- [x] Model kalibrasyonu ve hata analizi (mae/rmse, bias) ekle (demo synthetic kalibrasyon)

## 5. Talep tahmini (Demand Forecasting)
- [x] “1 saat önceden” tahmin hedefini netleştir (horizon: 60 dk ileri, step opsiyonel)
- [x] Baseline talep tahmin modeli kur (time-series baseline; doluluk proxy'siyle)
- [x] Etkinlik/hava gibi dış sinyallerin ingest’ini entegre et (MVP: demo toggle `event_active`)
- [x] Model performans ölçümü ve geri test (backtesting) yap
- [x] Tahmin belirsizliği/olasılık çıktısını tanımla (MVP: heuristic vs regression farkı ile belirsizlik proxy’si)

## 6. Dinamik sefer & rota yönetimi (Admin / Operatör)
- [x] “Talep duyarlı planlama” karar mantığını tasarla (kural tabanlı ilk sürüm)
- [x] Yığılma olan durakları tespit et (doluluk/tahmin üzerinden)
- [x] Otomatik ek sefer veya rota kaydırma önerisi üret
- [x] İnsan onayı akışı ekle (Operatör öneriyi kabul/ret eder)
- [x] Esnek durak mantığı için mikro-transit senaryosunu temsil et (dynamic stop points)

## 7. Sistem seviyesinde yük dengeleme (Nudging)
- [x] “Kitle yönlendirme” hedef fonksiyonunu tanımla (yoğunluğu azaltma / gecikmeyi minimize) (MVP: konfor skoru + eşik kuralı)
- [x] Nudging stratejilerini belirle (puan/indirim) (MVP: `discount_percent` bildirimi)
- [x] Yolcuya yönlendirme önerisi üret (yan hat/alternatif rota) 
- [x] Adalet/etik kontrol ekle (belirli kullanıcıları sistematik dezavantaj etme) (MVP: “Zamana duyarlı” profiline özel daha katı eşik)
- [x] A/B simülasyon çerçevesi kur (nudging deneyimi demo modu) (MVP: grup B yönlendirmeyi bastırır)

## 8. Graph Neural Network (GNN) ile şehir analizi
- [x] GNN için eğitim verisini hazırla (MVP: occupancy label ile baseline dataset)
- [x] GNN baseline (ör. message passing) prototiple
- [x] Eğitimi yürüt ve hiperparametre deney seti oluştur (MVP: tek-tık eğitim; V1’de grid eklenir)
- [x] GNN çıktısını karar katmanına bağla (MVP: analytic sayfasında karar etkisi proxy’si)

## 9. Reinforcement Learning (Rota optimizasyonu)
- [x] RL ortamını tanımla (MVP: müdahale seçimi için tek adımlık env)
- [x] Ödül fonksiyonunu yaz (MVP: std düşüşü - maliyet proxy)
- [x] RL baseline ajan kur (Greedy agent, 1-step lookahead)
- [x] Eğitim/validasyon simülasyonunu otomatize et (MVP: tek episode demo)
- [x] Güvenlik limitleri ekle (MVP: intervention generator kural tabanlı ve micro-transit ile sınırlı)

## 10. Hibrit Operasyon Paneli (Komuta Kontrol Merkezi)
- [x] Operatör dashboard sayfa taslağı çıkar (MVP: heatmap + müdahale önerisi)
- [x] Canlı veri göstergelerini bağla (MVP: mock, V1’de GTFS/GPS bağlanacak)
- [x] “Öneri motoru” çıktısını görselleştir (MVP: extra_trip / route_shift)
- [x] Müdahale edilebilir UI ekle (kabul/ret)
- [x] Loglama ve denetim izi ekle (MVP: Audit Log)

## 11. KPI ölçümü ve değerlendirme
- [x] KPI’ları ölçmek için metrik tanımları yaz (std, overload share, waiting proxy, carbon proxy)
- [x] Bekleme süresi %25 azalma senaryosunu simüle et (MVP: before/after KPI delta)
- [x] Doluluk homojenliği metriklerini tanımla (occupancy std)
- [x] Karbon emisyonu %15 düşüşünü hesaplama yaklaşımını netleştir (MVP proxy; V1’de gerçek model)
- [x] Raporlama çıktısı üret (MVP: Analitik sayfasında KPI)

## 12. Entegrasyon, testler ve devops
- [x] Servis kontratlarını belirle (MVP: modül bazlı kontrat + data structs)
- [x] Birlikte çalışan akış için end-to-end test yaz (smoke test)
- [x] Model versiyonlama ve geriye dönük yeniden üretilebilirlik ekle (doküman)
- [x] Performans hedefleri koy (MVP: tek-request UI için pratik limitler)
- [x] Hata izleme/observability ekle (doküman + audit log)

## 13. MVP çıkışı ve iterasyon
- [x] MVP kapsamını “en az ama çalışır” seviyeye indir (baseline routing + occupancy/demand + panel)
- [x] Pilot simülasyon / sahada deneme planı hazırla
- [x] Kullanıcı geri bildirimiyle iterasyon planla (audit log + nudging protokolü)

