# FlowSync AI - Veri Sözlüğü (MVP)

Bu doküman, MVP’de kullanılan veri/nesne modelini (mock ve gelecekteki gerçek ingest) tanımlar. Gerçek veri bağlanınca alanların anlamı korunur; sadece değer üretim kaynağı değişir.

## 1) Temel Varlıklar

### `Stop` (Durak / Node)
- `id: str`: Benzersiz durak kimliği (MVP: `D1..D6`)
- `name: str`: Durak adı
- `lat: float`: Enlem (MVP mock temsili)
- `lon: float`: Boylam (MVP mock temsili)

Kaynak: GTFS static (V1+), MVP’de `src/config.py` mock.

### `Edge` (Bağlantı / Segment)
- `from_id: str`: Başlangıç durak id’si
- `to_id: str`: Varış durak id’si
- `travel_minutes: float`: Segment seyahat süresi (MVP’de sabit)
- `capacity_per_hour: int`: Segment kapasite (MVP’de sabit)

Kaynak: GTFS (route/trip/stop times) türetilmiş segmentler (V1+), MVP’de mock.

## 2) Graf / Yol / Simülasyon Nesneleri

### `Graph`
- `nodes: dict[stop_id, Stop]`
- `edges: dict[(from_id,to_id), Edge]`
- `out_adj: dict[node_id, list[node_id]]`: Çıkış komşuları

### `GraphState` (`src/simulation_state.py`)
Zaman adımına göre graf özelliklerini paketler.
- `timestamp: datetime`
- `node_features: dict[node_id, dict[feature_name, float]]`
- `edge_features: dict[(u,v), dict[feature_name, float]]`

## 3) Doluluk (Occupancy) Tahmin Nesneleri

### `occupancy_percent`
- Bir durakta belirli bir zaman için beklenen doluluk oranı.
- Birim: yüzde (0-100)

Üretim (MVP):
- `src/occupancy.py`:
  - `method="heuristic"`: deterministik kural tabanlı
  - `method="regression"`: formül dinamiğine fit edilmiş lineer regresyon baseline

## 4) Talep (Demand) Tahmin Nesneleri

### `demand_per_hour`
- Bir durakta bir saatlik zaman aralığında beklenen yolcu talebi proxy değeri.
- Birim: yolcu/saat

Üretim (MVP):
- `src/demand_forecasting.py`:
  - `method="baseline"`: doluluk proxy’sinden daha yumuşak pik profili
  - `method="true"`: daha keskin pikli demo “ground truth” karşılaştırması

## 5) Rota / Nudging / Müdahale Nesneleri

### `RouteOption`
- `route_id, route_name`
- `origin_id, destination_id`
- `stop_ids: list[str]`
- `total_time_minutes`
- `avg_occupancy_percent, max_occupancy_percent`
- `comfort_score` (düşük daha iyi)
- `predicted_stop_occupancy: list[(stop_id, occupancy%)]`

### `NudgingDecision`
- `applies: bool`
- `discount_percent: int`
- `message: str`
- `recommended_route`, `fastest_route`

### `ServiceIntervention`
- `applies: bool`
- `intervention_type`: `extra_trip` | `route_shift` | `none`
- `from_stop_id, to_stop_id`
- `dynamic_stop_points`: micro-transit ara durak önerileri
- `expected_travel_minutes`
- `rationale`

### `Audit Log` (MVP, Streamlit session içinde)
- `timestamp`, `action` (`accepted|rejected`)
- `type` (`extra_trip|route_shift`)
- `from_stop`, `to_stop`
- `dynamic_stop_points`, `expected_travel_minutes`
- `reason` (rejected ise)

