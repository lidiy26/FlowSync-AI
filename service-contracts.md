# FlowSync AI - Servis Kontratları (MVP)

Bu doküman, mevcut kod tabanındaki modüller arası “veri kontratlarını” özetler. Gerçek servis/microservice mimarisine geçildiğinde aynı sözleşmeler korunmalıdır.

## Model Layer

### Occupancy Forecast
- Fonksiyon: `predict_stop_occupancy_percent(stop_id, dt, event_active, route_context_factor, method, noise_enabled) -> float`
- Çıktı: `occupancy_percent` (0-100 arası)

### Demand Forecast
- Fonksiyon: `build_demand_timeseries_dataframe(stops, start_dt, horizon_minutes, step_minutes, event_active, route_context_factor, method) -> DataFrame`
- Çıktı: `demand_per_hour` (yolcu/saat proxy)

## Decision / Optimization

### Rota seçenekleri
- Fonksiyon: `get_route_options(origin_id, destination_id, departure_dt, event_active, stops, edges, route_templates) -> List[RouteOption]`

### Nudging
- Fonksiyon: `get_nudging_decision(routes, high_crowding_threshold_percent, discount_percent, time_sensitive) -> NudgingDecision`

### Service planning
- Fonksiyon: `plan_service_intervention(departure_dt, event_active, stops, edges, overload_threshold_percent, ...) -> ServiceIntervention`

## UI / Panel
- Operatör audit log: Streamlit `st.session_state["interventions_log"]` içinde tutulur.

