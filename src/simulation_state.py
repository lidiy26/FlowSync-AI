from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd

from .config import Edge, Stop
from .graph import Graph, get_edge_features, get_node_features, build_graph


@dataclass(frozen=True)
class GraphState:
    """
    Zaman adımı -> graf durumu.

    - node_features: node_id -> özellikler
    - edge_features: (u,v) -> özellikler
    """

    timestamp: datetime
    node_features: Dict[str, Dict[str, float]]
    edge_features: Dict[Tuple[str, str], Dict[str, float]]

    def to_node_features_dataframe(self) -> pd.DataFrame:
        rows = []
        for node_id, feats in self.node_features.items():
            row = {"node_id": node_id}
            row.update(feats)
            rows.append(row)
        return pd.DataFrame(rows)

    def to_edge_features_dataframe(self) -> pd.DataFrame:
        rows = []
        for (u, v), feats in self.edge_features.items():
            row = {"from_id": u, "to_id": v}
            row.update(feats)
            rows.append(row)
        return pd.DataFrame(rows)


def build_graph_state_at(
    *,
    timestamp: datetime,
    stops: List[Stop],
    edges: List[Edge],
    event_active: bool,
) -> GraphState:
    graph: Graph = build_graph(stops=stops, edges=edges)

    node_features: Dict[str, Dict[str, float]] = {}
    for stop_id, stop in graph.nodes.items():
        # stop_lat/lon için Graph içindeki Stop'u kullanıyoruz.
        feats = get_node_features(stop_id=stop_id, dt=timestamp, event_active=event_active)
        feats["stop_lat"] = float(stop.lat)
        feats["stop_lon"] = float(stop.lon)
        node_features[stop_id] = feats

    edge_features: Dict[Tuple[str, str], Dict[str, float]] = {}
    for edge_id, edge in graph.edges.items():
        edge_features[edge_id] = get_edge_features(edge=edge)

    return GraphState(
        timestamp=timestamp,
        node_features=node_features,
        edge_features=edge_features,
    )


def build_graph_states_over_horizon(
    *,
    departure_dt: datetime,
    step_minutes: int,
    horizon_minutes: int,
    stops: List[Stop],
    edges: List[Edge],
    event_active: bool,
) -> List[GraphState]:
    if step_minutes <= 0:
        raise ValueError("step_minutes must be > 0")
    if horizon_minutes < 0:
        raise ValueError("horizon_minutes must be >= 0")

    states: List[GraphState] = []
    for offset in range(0, horizon_minutes + 1, step_minutes):
        states.append(
            build_graph_state_at(
                timestamp=departure_dt + timedelta(minutes=offset),
                stops=stops,
                edges=edges,
                event_active=event_active,
            )
        )
    return states

