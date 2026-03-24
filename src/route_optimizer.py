from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

from .config import Edge, Stop
from .occupancy import predict_stop_occupancy_percent
from .graph import build_graph, iter_simple_paths, route_total_travel_time_minutes


@dataclass(frozen=True)
class RouteOption:
    route_id: str
    route_name: str
    origin_id: str
    destination_id: str
    stop_ids: List[str]
    total_time_minutes: float
    avg_occupancy_percent: float
    max_occupancy_percent: float
    comfort_score: float
    predicted_stop_occupancy: List[Tuple[str, float]]  # (stop_id, occupancy%)


def _stable_route_name(route_id: str) -> str:
    return {
        "R1": "Ana Hat",
        "R2": "Alternatif Hat 1",
        "R3": "Alternatif Hat 2",
        "R4": "Alternatif Hat 3",
    }.get(route_id, route_id)


def _compute_route_time_minutes(
    stop_ids: List[str],
    edge_lookup: Dict[Tuple[str, str], Edge],
) -> float:
    total = 0.0
    for u, v in zip(stop_ids, stop_ids[1:]):
        edge = edge_lookup.get((u, v))
        if edge is None:
            raise ValueError(f"Edge bulunamadı: {u}->{v}")
        total += edge.travel_minutes
    return total


def _route_context_factor(stop_ids: List[str]) -> float:
    # Daha fazla durak = daha fazla dur-kalk = “beklenen” doluluk algısı artar.
    # MVP seviyesinde kaba ve deterministik bir çarpan kullanıyoruz.
    segments = max(1, len(stop_ids) - 1)
    return 0.92 + 0.05 * segments


def _predict_route_occupancy(
    *,
    stop_ids: List[str],
    origin_id: str,
    destination_id: str,
    departure_dt: datetime,
    event_active: bool,
    edge_lookup: Dict[Tuple[str, str], Edge],
) -> List[Tuple[str, float]]:
    # Her durak için ETA'ya göre doluluk tahmini yap.
    context_factor = _route_context_factor(stop_ids)
    predicted: List[Tuple[str, float]] = []

    elapsed = 0.0
    for idx, stop_id in enumerate(stop_ids):
        if idx > 0:
            prev = stop_ids[idx - 1]
            edge = edge_lookup[(prev, stop_id)]
            elapsed += edge.travel_minutes
        # ETA kaydır: duraktan varış zamanını hesapla.
        dt_at_stop = datetime.fromtimestamp(
            departure_dt.timestamp() + elapsed * 60.0
        ).replace(microsecond=0)
        occ = predict_stop_occupancy_percent(
            stop_id=stop_id,
            dt=dt_at_stop,
            event_active=event_active,
            route_context_factor=context_factor,
        )
        predicted.append((stop_id, occ))
    return predicted


def _comfort_score(total_time_minutes: float, predicted_stop_occupancy: List[Tuple[str, float]]) -> float:
    occ_values = [v for _, v in predicted_stop_occupancy]
    avg_occ = sum(occ_values) / max(1, len(occ_values))
    max_occ = max(occ_values) if occ_values else 0.0

    # Lower = better
    # Zamanı temel al, sonra ortalama ve maksimum doluluğu “cezalandır”.
    return float(total_time_minutes) + (avg_occ / 100.0) * 60.0 + (max_occ / 100.0) * 20.0


def get_route_options(
    *,
    origin_id: str,
    destination_id: str,
    departure_dt: datetime,
    event_active: bool,
    stops: List[Stop],
    edges: List[Edge],
    route_templates: Dict[str, List[str]] | None = None,
    max_options: int = 3,
) -> List[RouteOption]:
    stops_lookup: Dict[str, Stop] = {s.id: s for s in stops}
    edge_lookup: Dict[Tuple[str, str], Edge] = {(e.from_id, e.to_id): e for e in edges}

    if origin_id not in stops_lookup or destination_id not in stops_lookup:
        return []
    if origin_id == destination_id:
        return []

    graph = build_graph(stops=stops, edges=edges)

    # Baseline rota çıkarımı: hem “şablon hatlar” hem de graf üzerinde basit path enumerasyonu.
    # (Template’ler MVP çeşitliliği sağlar; graph path’ler temel “heuristic baseline”dir.)
    raw_candidates: List[Dict[str, object]] = []

    if route_templates:
        for route_id, template_stops in route_templates.items():
            if origin_id not in template_stops or destination_id not in template_stops:
                continue

            o_idx = template_stops.index(origin_id)
            d_idx = template_stops.index(destination_id)
            if o_idx >= d_idx:
                continue

            stop_ids = template_stops[o_idx : d_idx + 1]
            raw_candidates.append(
                {
                    "route_id": route_id,
                    "route_name": _stable_route_name(route_id),
                    "stop_ids": stop_ids,
                    "source": "template",
                }
            )

    path_limit = max(10, max_options * 4)
    max_hops = 4  # MVP için küçük graflarda yeterli çeşitlilik
    for path_idx, stop_ids in enumerate(
        iter_simple_paths(
            graph,
            origin_id=origin_id,
            destination_id=destination_id,
            max_hops=max_hops,
            max_paths=path_limit,
        ),
        start=1,
    ):
        total_time = route_total_travel_time_minutes(
            route_stop_ids=stop_ids,
            edge_lookup=edge_lookup,
        )
        if total_time is None:
            continue

        raw_candidates.append(
            {
                "route_id": f"P{path_idx}",
                "route_name": f"Heuristic Hat {path_idx}",
                "stop_ids": stop_ids,
                "source": "graph",
            }
        )

    # Aynı durak dizisini (stop_ids) tekrar tekrar eklememek için dedup.
    seen = set()
    candidates: List[RouteOption] = []
    for rc in raw_candidates:
        stop_ids = rc["stop_ids"]  # type: ignore[assignment]
        stop_ids_tuple = tuple(stop_ids)  # type: ignore[arg-type]
        if stop_ids_tuple in seen:
            continue
        seen.add(stop_ids_tuple)

        try:
            total_time = _compute_route_time_minutes(stop_ids, edge_lookup)  # type: ignore[arg-type]
        except ValueError:
            continue

        predicted_occ = _predict_route_occupancy(
            stop_ids=list(stop_ids),  # type: ignore[arg-type]
            origin_id=origin_id,
            destination_id=destination_id,
            departure_dt=departure_dt,
            event_active=event_active,
            edge_lookup=edge_lookup,
        )

        occ_values = [v for _, v in predicted_occ]
        avg_occ = sum(occ_values) / max(1, len(occ_values))
        max_occ = max(occ_values) if occ_values else 0.0

        comfort = _comfort_score(total_time, predicted_occ)

        candidates.append(
            RouteOption(
                route_id=str(rc["route_id"]),
                route_name=str(rc["route_name"]),
                origin_id=origin_id,
                destination_id=destination_id,
                stop_ids=list(stop_ids),  # type: ignore[arg-type]
                total_time_minutes=total_time,
                avg_occupancy_percent=avg_occ,
                max_occupancy_percent=max_occ,
                comfort_score=comfort,
                predicted_stop_occupancy=predicted_occ,
            )
        )

    candidates.sort(key=lambda r: (r.comfort_score, r.total_time_minutes))
    return candidates[:max_options]


def pick_main_and_fastest(routes: List[RouteOption]) -> Tuple[RouteOption | None, RouteOption | None]:
    if not routes:
        return None, None
    # “Ana” rota: konfor skoru en iyi (daha az kalabalık + makul süre)
    by_comfort = min(routes, key=lambda r: r.comfort_score)
    # “En hızlı” rota: sadece süreye göre
    by_time = min(routes, key=lambda r: r.total_time_minutes)
    return by_comfort, by_time

