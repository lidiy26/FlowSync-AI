from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict

from .types import IngestEvent
from ..config import get_mock_stops


def ingest_gps_mock(
    *,
    start_dt: datetime,
    horizon_minutes: int = 60,
    step_minutes: int = 10,
) -> List[IngestEvent]:
    """
    MVP mock GPS ingest:
    - Her durak için temsili “araç yakınlığı” event’i üretir.
    - V1’de gerçek GPS time-series event’lerine döner.
    """
    stops = get_mock_stops()
    events: List[IngestEvent] = []
    times = list(range(0, horizon_minutes + 1, step_minutes))
    for t in times:
        ts = start_dt + timedelta(minutes=t)
        for idx, s in enumerate(stops):
            # Simülasyon: duraklara araç yoğunluğu sinusoidal.
            events.append(
                IngestEvent(
                    source="gps_mock",
                    timestamp=ts,
                    route_id=None,
                    trip_id=None,
                    vehicle_id=f"GPS_V{idx}",
                    stop_id=s.id,
                    lat=s.lat + 0.001 * (idx % 3),
                    lon=s.lon + 0.001 * (idx % 2),
                    payload={"vehicle_proximity": float((idx % 4) / 3.0)},
                )
            )
    return events

