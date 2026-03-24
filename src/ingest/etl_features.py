from __future__ import annotations

from typing import List, Dict

import pandas as pd

from .types import IngestEvent


def build_model_features_from_events_mock(events: List[IngestEvent]) -> "pd.DataFrame":
    """
    MVP ETL şeması (mock):
    - stop_id ve timestamp üzerinden agregasyon
    - mobile_signal payload'den `anonymous_crowd_index` alıp occupancy/demand proxy üret
    """
    records: List[Dict[str, object]] = []
    for e in events:
        if e.stop_id is None:
            continue
        crowd_idx = e.payload.get("anonymous_crowd_index", None)
        vehicle_proximity = e.payload.get("vehicle_proximity", None)
        if crowd_idx is None and vehicle_proximity is None:
            continue

        crowd_idx_f = float(crowd_idx) if crowd_idx is not None else 0.0
        prox_f = float(vehicle_proximity) if vehicle_proximity is not None else 0.0

        occupancy_proxy = max(5.0, min(98.0, 20.0 + crowd_idx_f * 60.0 + prox_f * 10.0))
        demand_proxy = max(0.0, occupancy_proxy / 100.0 * 200.0)

        records.append(
            {
                "timestamp": e.timestamp,
                "stop_id": e.stop_id,
                "occupancy_proxy_percent": occupancy_proxy,
                "demand_proxy_per_hour": demand_proxy,
            }
        )

    if not records:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "stop_id",
                "occupancy_proxy_percent",
                "demand_proxy_per_hour",
            ]
        )

    df = pd.DataFrame(records)
    df = df.groupby(["timestamp", "stop_id"], as_index=False).mean(numeric_only=True)
    return df.sort_values(["stop_id", "timestamp"])

