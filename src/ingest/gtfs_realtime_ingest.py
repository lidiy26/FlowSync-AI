from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .types import IngestEvent
from ..config import get_mock_edges, get_mock_stops


def ingest_gtfs_realtime_mock(
    *,
    start_dt: datetime,
    horizon_minutes: int = 60,
    step_minutes: int = 10,
) -> List[IngestEvent]:
    """
    MVP mock GTFS-Realtime ingest:
    - Araç konumları (lat/lon) ve seyir bilgisi için temsilî event üretir.
    - V1’de real GTFS-Realtime endpoint mapper ile değiştirilecek.
    """
    stops = get_mock_stops()
    stop_lookup: Dict[str, object] = {s.id: s for s in stops}
    edges = get_mock_edges()

    events: List[IngestEvent] = []
    times = list(range(0, horizon_minutes + 1, step_minutes))
    for t in times:
        ts = start_dt + timedelta(minutes=t)
        for idx, e in enumerate(edges):
            u = stop_lookup[e.from_id]
            v = stop_lookup[e.to_id]
            # İki durak arasında lineer ilerleme (temsili).
            alpha = (t % max(1, step_minutes)) / float(max(1, step_minutes))
            lat = float(getattr(u, "lat")) * (1 - alpha) + float(getattr(v, "lat")) * alpha
            lon = float(getattr(u, "lon")) * (1 - alpha) + float(getattr(v, "lon")) * alpha
            events.append(
                IngestEvent(
                    source="gtfs_realtime_mock",
                    timestamp=ts,
                    route_id=f"R{(idx % 4) + 1}",
                    trip_id=f"T{idx}",
                    vehicle_id=f"V{idx}",
                    stop_id=None,
                    lat=lat,
                    lon=lon,
                    payload={"speed_kmh": 25 + (idx % 7)},
                )
            )
    return events

