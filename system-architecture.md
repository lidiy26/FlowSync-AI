# FlowSync AI - Sistem Mimarisi (MVP/V1)

## 1) Bileşenler
1. **UI (Streamlit)**: Yolcu & Operatör ekranları, metrik/öneri gösterimi, insan onayı.
2. **Karar/Optimizasyon Mantığı (Decision Engine)**:
   - Rota seçenek üretimi (`src/route_optimizer.py`)
   - Nudging (`src/nudging.py`)
   - Dinamik sefer/rota planlama (`src/service_planning.py`)
3. **Tahmin Servisleri (Model Layer)**:
   - Doluluk tahmini (`src/occupancy.py`)
   - Talep tahmini (`src/demand_forecasting.py`)
4. **Graf Temsil & Simülasyon**:
   - Şehir ağı (`src/graph.py`)
   - Zaman adımı graf özellikleri (`src/simulation_state.py`)
5. **AI Açıklama (Gemini opsiyonel)**: Sadece özet metin üretimi (`src/gemini_client.py`)

## 2) Veri Akışı
1. Kullanıcı girdileri (origin, destination, kalkış zamanı) UI üzerinden gelir.
2. Graph ve mock/gerçek kaynaklardan feature üretimi yapılır.
3. Model layer:
   - rota seçenekleri üzerinden durak bazında occupancy tahmini
   - durak bazında demand tahmini
4. Nudging/Service planning:
   - yoğunluk eşiği + konfor/fairness hedefleriyle öneri üretimi
5. İnsan onayı:
   - operatör “kabul/reddet” seçer ve audit log güncellenir.

## 3) Modüler Tasarım Notu
- UI sadece “render” eder; tahmin ve karar mantığı `src/` modüllerinde izole edilir.
- V1’de ingest bağlandığında:
  - mock `config.py` yerini GTFS-Realtime/GPS/mobil sinyal ingest mapper’ları alır.

