from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .config import Edge, Stop
from .occupancy import predict_stop_occupancy_percent


@dataclass(frozen=True)
class ExtraTripRecommendation:
    applies: bool
    from_stop_id: Optional[str]
    to_stop_id: Optional[str]
    expected_travel_minutes: Optional[float]
    rationale: str


def build_stop_heatmap_dataframe(
    *,
    departure_dt: datetime,
    event_active: bool,
    stops: List[Stop],
    edges: List[Edge],
    horizon_minutes: int = 30,
) -> pd.DataFrame:
    dt_heat = departure_dt + timedelta(minutes=horizon_minutes)
    rows = []
    for s in stops:
        occ = predict_stop_occupancy_percent(
            stop_id=s.id,
            dt=dt_heat,
            event_active=event_active,
            route_context_factor=1.0,
        )
        rows.append({"Durak": s.name, "Durak ID": s.id, "Beklenen Doluluk (%)": occ})

    return pd.DataFrame(rows).sort_values("Beklenen Doluluk (%)", ascending=False)


def style_heatmap_traffic(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    # Yüksek doluluk = daha kırmızı.
    styler = df.copy()
    styler = styler.drop(columns=["Durak ID"], errors="ignore")
    return styler.style.background_gradient(
        subset=["Beklenen Doluluk (%)"],
        cmap="RdYlGn",
        axis=0,
    ).format({"Beklenen Doluluk (%)": "{:.0f}%"})


def get_extra_trip_recommendation(
    *,
    departure_dt: datetime,
    event_active: bool,
    stops: List[Stop],
    edges: List[Edge],
    overload_threshold_percent: float,
) -> ExtraTripRecommendation:
    dt_future = departure_dt + timedelta(minutes=30)

    stops_lookup: Dict[str, Stop] = {s.id: s for s in stops}
    edge_lookup: Dict[Tuple[str, str], Edge] = {(e.from_id, e.to_id): e for e in edges}

    occ_by_stop = {
        s.id: predict_stop_occupancy_percent(
            stop_id=s.id,
            dt=dt_future,
            event_active=event_active,
            route_context_factor=1.0,
        )
        for s in stops
    }

    overload_stops = [sid for sid, occ in occ_by_stop.items() if occ >= overload_threshold_percent]
    if not overload_stops:
        return ExtraTripRecommendation(
            applies=False,
            from_stop_id=None,
            to_stop_id=None,
            expected_travel_minutes=None,
            rationale="Öneri için eşik aşımı yok.",
        )

    # En yüksek doluluk durak -> en düşük komşu durak öner.
    from_stop_id = max(overload_stops, key=lambda sid: occ_by_stop[sid])
    neighbors = [e.to_id for e in edges if e.from_id == from_stop_id]
    if not neighbors:
        return ExtraTripRecommendation(
            applies=True,
            from_stop_id=from_stop_id,
            to_stop_id=None,
            expected_travel_minutes=None,
            rationale="Komşu durak bilgisi demo verisinde bulunamadı.",
        )

    to_stop_id = min(neighbors, key=lambda sid: occ_by_stop[sid])
    travel = None
    edge = edge_lookup.get((from_stop_id, to_stop_id))
    if edge is not None:
        travel = float(edge.travel_minutes)

    return ExtraTripRecommendation(
        applies=True,
        from_stop_id=from_stop_id,
        to_stop_id=to_stop_id,
        expected_travel_minutes=travel,
        rationale=(
            f"{stops_lookup[from_stop_id].name} durak yoğunluğu eşik üstünde. "
            f"Yakındaki {stops_lookup[to_stop_id].name} daha düşük yoğunlukta."
        ),
    )

