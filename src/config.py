from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Stop:
    id: str
    name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class Edge:
    from_id: str
    to_id: str
    travel_minutes: float
    capacity_per_hour: int


def get_mock_stops() -> List[Stop]:
    # Koordinatlar sadece görselleştirme/ısı haritası için “temsili”dir.
    return [
        Stop("D1", "Durak A", 41.00, 29.00),
        Stop("D2", "Durak B", 41.01, 29.01),
        Stop("D3", "Durak C", 41.02, 29.02),
        Stop("D4", "Durak D", 41.03, 29.03),
        Stop("D5", "Durak E", 41.02, 29.04),
        Stop("D6", "Durak F", 40.99, 29.02),
    ]


def get_mock_edges() -> List[Edge]:
    return [
        Edge("D1", "D2", 6.0, 500),
        Edge("D2", "D3", 8.0, 520),
        Edge("D3", "D4", 7.0, 480),
        Edge("D2", "D5", 10.0, 450),
        Edge("D5", "D4", 6.5, 470),
        Edge("D1", "D6", 9.0, 460),
        Edge("D6", "D3", 5.5, 500),
        # Alternatif “daha az yoğun” için rota seçenekleri sağlayan ekstra bağlar
        Edge("D6", "D5", 7.5, 410),
    ]


def get_mock_route_templates() -> Dict[str, List[str]]:
    # Her şablon bir rota adımıdır (durak id listesi).
    return {
        "R1": ["D1", "D2", "D3", "D4"],  # “ana hat”
        "R2": ["D1", "D2", "D5", "D4"],  # alternatif 1
        "R3": ["D1", "D6", "D3", "D4"],  # alternatif 2
        "R4": ["D1", "D6", "D5", "D4"],  # alternatif 3
    }


def get_default_nudging_threshold_percent() -> float:
    return 70.0


def get_default_nudging_discount_percent() -> int:
    return 20


def get_default_ai_enabled() -> bool:
    return True


def get_default_debug_default() -> bool:
    return False


def build_lookup_stops(stops: List[Stop]) -> Dict[str, Stop]:
    return {s.id: s for s in stops}


def build_lookup_edges(edges: List[Edge]) -> Dict[Tuple[str, str], Edge]:
    return {(e.from_id, e.to_id): e for e in edges}

