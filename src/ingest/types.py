from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass(frozen=True)
class IngestEvent:
    source: str
    timestamp: datetime
    route_id: Optional[str]
    trip_id: Optional[str]
    vehicle_id: Optional[str]
    stop_id: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    payload: Dict[str, float | int | str | bool | None]

