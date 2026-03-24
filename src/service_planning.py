from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Optional, Tuple

from .config import Edge, Stop
from .occupancy import predict_stop_occupancy_percent
from .route_optimizer import get_route_options, pick_main_and_fastest


@dataclass(frozen=True)
class ServiceIntervention:
    applies: bool
    intervention_type: Literal["none", "extra_trip", "route_shift"]
    from_stop_id: Optional[str]
    to_stop_id: Optional[str]
    dynamic_stop_points: List[str]
    expected_travel_minutes: Optional[float]
    rationale: str

    predicted_from_peak_occ: Optional[float]
    predicted_to_peak_occ: Optional[float]
    suggested_route_name: Optional[str]


def _edge_travel_minutes(
    *,
    from_id: str,
    to_id: str,
    edges: List[Edge],
) -> Optional[float]:
    edge_map: Dict[Tuple[str, str], Edge] = {(e.from_id, e.to_id): e for e in edges}
    edge = edge_map.get((from_id, to_id))
    if edge is None:
        return None
    return float(edge.travel_minutes)


def plan_service_intervention(
    *,
    departure_dt: datetime,
    event_active: bool,
    stops: List[Stop],
    edges: List[Edge],
    overload_threshold_percent: float,
    route_context_factor: float = 1.0,
    planning_horizon_minutes: int = 30,
    max_route_shift_options: int = 3,
) -> ServiceIntervention:
    """
    Kural tabanlı MVP planlayıcı:
    - Yığılma: `planning_horizon_minutes` sonra durak doluluğu >= eşik ise overload.
    - En yoğun overload durak (from).
    - Komşu/neighbor düşük dolulukta ise (to) extra trip veya rota kaydırma.
    - Micro-transit (dynamic stop points): rota shift önerisinde ara durakları döndürür.
    """
    if planning_horizon_minutes < 0:
        raise ValueError("planning_horizon_minutes must be >= 0")

    dt_future = departure_dt + timedelta(minutes=planning_horizon_minutes)

    stops_lookup: Dict[str, Stop] = {s.id: s for s in stops}
    if not stops_lookup:
        return ServiceIntervention(
            applies=False,
            intervention_type="none",
            from_stop_id=None,
            to_stop_id=None,
            dynamic_stop_points=[],
            expected_travel_minutes=None,
            rationale="Durak verisi yok.",
            predicted_from_peak_occ=None,
            predicted_to_peak_occ=None,
            suggested_route_name=None,
        )

    # Durak doluluklarını tahmin et.
    occ_by_stop: Dict[str, float] = {}
    for s in stops:
        occ_by_stop[s.id] = predict_stop_occupancy_percent(
            stop_id=s.id,
            dt=dt_future,
            event_active=event_active,
            route_context_factor=route_context_factor,
            method="regression",
            noise_enabled=False,
        )

    overload_stops = [sid for sid, occ in occ_by_stop.items() if occ >= overload_threshold_percent]
    if not overload_stops:
        return ServiceIntervention(
            applies=False,
            intervention_type="none",
            from_stop_id=None,
            to_stop_id=None,
            dynamic_stop_points=[],
            expected_travel_minutes=None,
            rationale="Yoğunluk eşiği aşılmadı.",
            predicted_from_peak_occ=None,
            predicted_to_peak_occ=None,
            suggested_route_name=None,
        )

    from_stop_id = max(overload_stops, key=lambda sid: occ_by_stop[sid])

    # “to” için neighbor seçimi: from_stop_id -> outgoing komşular içinden en düşük doluluk.
    outgoing_neighbors = [e.to_id for e in edges if e.from_id == from_stop_id]
    outgoing_neighbors = sorted(set(outgoing_neighbors))
    if not outgoing_neighbors:
        return ServiceIntervention(
            applies=True,
            intervention_type="extra_trip",
            from_stop_id=from_stop_id,
            to_stop_id=None,
            dynamic_stop_points=[],
            expected_travel_minutes=None,
            rationale="Komşu durak bilgisi bulunamadı. Extra trip düşünülür.",
            predicted_from_peak_occ=occ_by_stop[from_stop_id],
            predicted_to_peak_occ=None,
            suggested_route_name=None,
        )

    to_stop_id = min(outgoing_neighbors, key=lambda sid: occ_by_stop[sid])

    predicted_from = occ_by_stop[from_stop_id]
    predicted_to = occ_by_stop[to_stop_id]
    travel = _edge_travel_minutes(from_id=from_stop_id, to_id=to_stop_id, edges=edges)

    # Rota kaydırmayı dene: from -> to arası rota seçeneklerini üret.
    route_shift_options = get_route_options(
        origin_id=from_stop_id,
        destination_id=to_stop_id,
        departure_dt=departure_dt,
        event_active=event_active,
        stops=stops,
        edges=edges,
        route_templates=None,
        max_options=max_route_shift_options,
    )

    route_shift_main, route_shift_fastest = pick_main_and_fastest(route_shift_options)

    if route_shift_main is None:
        # Rota shift üretilemezse extra trip.
        extra_kind = "extra_trip"
        rationale = (
            f"{stops_lookup[from_stop_id].name} durak yoğunluğu eşiği aşıyor. "
            f"Yakındaki {stops_lookup[to_stop_id].name} durak daha düşük yoğunlukta; "
            f"ek sefer önerilir."
        )
        return ServiceIntervention(
            applies=True,
            intervention_type=extra_kind,
            from_stop_id=from_stop_id,
            to_stop_id=to_stop_id,
            dynamic_stop_points=[],
            expected_travel_minutes=travel,
            rationale=rationale,
            predicted_from_peak_occ=predicted_from,
            predicted_to_peak_occ=predicted_to,
            suggested_route_name=None,
        )

    # Micro-transit (dynamic stop points) için ara durakları öner.
    dynamic_points = [sid for sid in route_shift_main.stop_ids[1:-1]]

    applies_route_shift = True
    rationale = (
        f"Yoğun {stops_lookup[from_stop_id].name} durak (beklenen %{predicted_from:.0f}) için "
        f"daha boş {stops_lookup[to_stop_id].name} yönüne rota kaydırma öneriyoruz. "
        f"Önerilen rota: “{route_shift_main.route_name}” (konfor odaklı)."
    )

    return ServiceIntervention(
        applies=applies_route_shift,
        intervention_type="route_shift",
        from_stop_id=from_stop_id,
        to_stop_id=to_stop_id,
        dynamic_stop_points=dynamic_points,
        expected_travel_minutes=travel,
        rationale=rationale,
        predicted_from_peak_occ=predicted_from,
        predicted_to_peak_occ=predicted_to,
        suggested_route_name=route_shift_main.route_name,
    )

