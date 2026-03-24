from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

from .config import Edge, Stop


@dataclass(frozen=True)
class Graph:
    nodes: Dict[str, Stop]
    edges: Dict[Tuple[str, str], Edge]
    out_adj: Dict[str, List[str]]

    def has_path(self, origin_id: str, destination_id: str) -> bool:
        if origin_id not in self.nodes or destination_id not in self.nodes:
            return False
        return origin_id == destination_id or destination_id in self.out_adj.get(origin_id, [])


def build_graph(*, stops: List[Stop], edges: List[Edge]) -> Graph:
    nodes = {s.id: s for s in stops}
    edges_lookup: Dict[Tuple[str, str], Edge] = {(e.from_id, e.to_id): e for e in edges}

    out_adj: Dict[str, List[str]] = {sid: [] for sid in nodes.keys()}
    for (u, v), _edge in edges_lookup.items():
        out_adj.setdefault(u, []).append(v)

    # Deterministiklik için
    for u in out_adj:
        out_adj[u] = sorted(set(out_adj[u]))

    return Graph(nodes=nodes, edges=edges_lookup, out_adj=out_adj)


def get_node_features(*, stop_id: str, dt: datetime, event_active: bool) -> Dict[str, float]:
    """
    MVP için “ölçülebilir”/“kullanılabilir” temel feature seti.
    Occupancy (doluluk) gibi daha ileri sinyaller adım 4 kapsamındadır.
    """
    hour = dt.hour + dt.minute / 60.0
    hour_norm = hour / 24.0

    return {
        "hour_sin": math.sin(2.0 * math.pi * hour_norm),
        "hour_cos": math.cos(2.0 * math.pi * hour_norm),
        "event_active": 1.0 if event_active else 0.0,
        # Konum feature'ları baseline'de GNN/heuristic için hazırlanır.
        # (lat/lon ölçek normalizasyonu ayrıca yapılabilir.)
        "stop_lat": 0.0,
        "stop_lon": 0.0,
    }


def get_edge_features(*, edge: Edge) -> Dict[str, float]:
    return {
        "travel_minutes": float(edge.travel_minutes),
        "capacity_per_hour": float(edge.capacity_per_hour),
    }


def iter_simple_paths(
    graph: Graph,
    *,
    origin_id: str,
    destination_id: str,
    max_hops: int,
    max_paths: int,
) -> Iterable[List[str]]:
    """
    Baseline rota çıkarımı: Basit (cycle içermeyen) en fazla `max_hops` kadar
    duraktan geçen yolları enumerate eder.
    """
    if origin_id == destination_id:
        return []
    if origin_id not in graph.nodes or destination_id not in graph.nodes:
        return []

    results: List[List[str]] = []
    stack: List[List[str]] = [[origin_id]]

    while stack and len(results) < max_paths:
        path = stack.pop()
        last = path[-1]
        hops = len(path) - 1

        if hops > max_hops:
            continue

        if last == destination_id:
            results.append(path)
            continue

        for nxt in graph.out_adj.get(last, []):
            if nxt in path:
                continue  # simple path
            stack.append(path + [nxt])

    return results


def route_stop_ids_to_edge_ids(route_stop_ids: List[str]) -> List[Tuple[str, str]]:
    return list(zip(route_stop_ids, route_stop_ids[1:]))


def route_total_travel_time_minutes(
    *,
    route_stop_ids: List[str],
    edge_lookup: Dict[Tuple[str, str], Edge],
) -> Optional[float]:
    total = 0.0
    for u, v in zip(route_stop_ids, route_stop_ids[1:]):
        edge = edge_lookup.get((u, v))
        if edge is None:
            return None
        total += float(edge.travel_minutes)
    return total

