# FlowSync AI - Observability (MVP)

## 1) Loglama
- Operatör öneri kabul/reddet aksiyonları: `Audit Log (MVP)` altında `st.session_state["interventions_log"]` formatında tutulur.
- Debug modu açıkken: graph/occupancy/demand ara değerleri ekranda gösterilir (UI gözlemlenebilirliği).

## 2) Metrikler
MVP’de metrikler UI üzerinden hesaplanır:
- Occupancy: MAE/RMSE/Bias (demo synthetic)
- Homojenlik: occupancy std
- Bekleme proxy: aşım fazlasından türetilen değer
- Carbon proxy: extra_trip/route_shift sayısından türetilir

## 3) Tracing
Gerçek dağıtık tracing MVP’de yoktur. V1+ için öneri:
- Her öneriye `request_id` atanır
- Aynı `request_id` ile model servis çağrıları ve UI audit logları ilişkilendirilir

