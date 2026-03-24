# FlowSync AI - Graph Temsili (MVP)

Bu doküman `tasks.md` içindeki 3. adım kapsamında oluşturulan graf temsilini özetler.

## 1. Temel Kavramlar
- **Node (durak)**: Şehir ağı üzerinde `Stop` ile temsil edilir (`id`, `name`, `lat`, `lon`).
- **Edge (bağlantı)**: İki durak arasındaki seyahat segmenti `Edge` ile temsil edilir (`from_id`, `to_id`, `travel_minutes`, `capacity_per_hour`).
- **Graph**: `Stop` node’ları ve `Edge` adjacency ilişkisiyle kurulur.

## 2. Feature Seti (Node / Edge)
### Node feature’ları (MVP)
- `hour_sin`, `hour_cos`: kalkış saatine bağlı zaman sinyali
- `event_active`: etkinlik/hava etkisi (demo toggle)
- `stop_lat`, `stop_lon`: durak konumu

### Edge feature’ları (MVP)
- `travel_minutes`: segment seyahat süresi
- `capacity_per_hour`: segment kapasitesi (baseline için)

> Not: Doluluk/yoğunluk gibi tahmin edilebilir sinyaller adım 4’te “occupancy estimation” kapsamına alınır; bu adımda temel zaman/konum/kapasite sinyalleri hazırlanır.

## 3. Baseline Rota Çıkarımı (Heuristic)
- Baseline için iki kaynak kullanılır:
  - Var ise `route_templates` (demo çeşitliliği)
  - Graf üzerinde `simple path` enumerasyonu (cycle içermeyen yollar)
- Rota alternatifleri:
  - `max_hops` kadar durak/bağlantı ile sınırlandırılır
  - `origin_id -> destination_id` arasında bulunan yollar aday olarak üretilir

## 4. Zaman Adımlı Veri: `timestamp -> graph state`
- Uygulamada `GraphState` ile bir zaman anında:
  - `node_features`: node_id -> feature map
  - `edge_features`: (u,v) -> feature map
  - `timestamp`: ilgili zaman
  - üretilir.
- `simulation_state.py`, belirli bir `step_minutes` ve `horizon_minutes` ile seri halde bir dizi `GraphState` üretir.

