from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from .types import IngestEvent


def normalize_events_mock(
    events: List[IngestEvent],
    *,
    time_granularity_minutes: int = 15,
) -> List[IngestEvent]:
    """
    MVP normalize:
    - timestamp’leri `time_granularity_minutes` ile “round” eder
    - payload içinde sayısal alanları float’a dönüştürür (proxy)
    """
    if time_granularity_minutes <= 0:
        raise ValueError("time_granularity_minutes must be > 0")

    def _round_dt(dt: datetime) -> datetime:
        epoch = dt.timestamp()
        step = time_granularity_minutes * 60.0
        rounded = round(epoch / step) * step
        return datetime.fromtimestamp(rounded)

    normalized: List[IngestEvent] = []
    for e in events:
        payload: Dict[str, float | int | str | bool | None] = dict(e.payload)
        for k, v in list(payload.items()):
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                payload[k] = float(v)
        normalized.append(
            IngestEvent(
                source=e.source,
                timestamp=_round_dt(e.timestamp),
                route_id=e.route_id,
                trip_id=e.trip_id,
                vehicle_id=e.vehicle_id,
                stop_id=e.stop_id,
                lat=e.lat,
                lon=e.lon,
                payload=payload,
            )
        )

    return normalized

