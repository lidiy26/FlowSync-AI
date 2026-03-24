from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Tuple

import numpy as np
import pandas as pd

from .occupancy import predict_stop_occupancy_percent


def _hour_float(dt: datetime) -> float:
    return dt.hour + dt.minute / 60.0


def _true_peak_total(hour: float) -> float:
    """
    "Ground truth" için daha keskin pik profili (baseline'dan farklı olsun diye).
    """
    morning = math.exp(-((hour - 8.0) / 1.6) ** 2)
    evening = 0.95 * math.exp(-((hour - 17.0) / 1.8) ** 2)
    return morning + evening


def _baseline_peak_total(hour: float) -> float:
    """
    Baseline için daha yumuşak pik profili.
    """
    morning = math.exp(-((hour - 8.0) / 2.4) ** 2)
    evening = 0.8 * math.exp(-((hour - 17.0) / 2.6) ** 2)
    return morning + evening


_STOP_DEMAND_BIAS: Dict[str, float] = {
    "D1": -0.08,
    "D2": 0.10,
    "D3": 0.16,
    "D4": -0.05,
    "D5": 0.07,
    "D6": 0.09,
}

_EVENT_DEMAND_BONUS: Dict[str, float] = {
    "D2": 0.20,
    "D3": 0.28,
    "D5": 0.16,
}


def true_stop_demand_per_hour(
    *,
    stop_id: str,
    dt: datetime,
    event_active: bool,
    route_context_factor: float = 1.0,
) -> float:
    """
    MVP demo için "talep" proxy'si: doluluk tahminini temel alıp,
    piki daha keskin yapan (baseline'dan farklı) bir ground-truth profili uygular.
    """
    # occupancy% -> ölçek (0..~98) => 10..200 arası yolcu/sa.
    occ = predict_stop_occupancy_percent(
        stop_id=stop_id,
        dt=dt,
        event_active=event_active,
        route_context_factor=route_context_factor,
        method="heuristic",
        noise_enabled=False,
    )
    occ_scale = 10.0 + (occ / 100.0) * 190.0

    hour = _hour_float(dt)
    peak = _true_peak_total(hour)

    stop_bias = _STOP_DEMAND_BIAS.get(stop_id, 0.0)
    event_bonus = _EVENT_DEMAND_BONUS.get(stop_id, 0.0) if event_active else 0.0

    # Keskin pik etkisi + bias.
    demand = occ_scale * (0.75 + 0.55 * peak) * (1.0 + stop_bias + event_bonus)

    # Güvenli aralık
    return float(max(0.0, min(350.0, demand)))


def baseline_stop_demand_forecast_per_hour(
    *,
    stop_id: str,
    dt: datetime,
    event_active: bool,
    route_context_factor: float = 1.0,
) -> float:
    """
    Baseline zaman-serisi model (MVP):
    - doluluk proxy'si
    - daha yumuşak pik profili
    - stop bias / event bonus
    """
    occ = predict_stop_occupancy_percent(
        stop_id=stop_id,
        dt=dt,
        event_active=event_active,
        route_context_factor=route_context_factor,
        method="regression",
        noise_enabled=False,
    )
    occ_scale = 10.0 + (occ / 100.0) * 190.0

    hour = _hour_float(dt)
    peak = _baseline_peak_total(hour)

    stop_bias = _STOP_DEMAND_BIAS.get(stop_id, 0.0)
    event_bonus = _EVENT_DEMAND_BONUS.get(stop_id, 0.0) if event_active else 0.0

    demand = occ_scale * (0.80 + 0.48 * peak) * (1.0 + stop_bias + 0.7 * event_bonus)
    return float(max(0.0, min(350.0, demand)))


def predict_demand_series(
    *,
    stop_id: str,
    start_dt: datetime,
    horizon_minutes: int,
    step_minutes: int,
    event_active: bool,
    route_context_factor: float = 1.0,
    method: Literal["baseline", "true"] = "baseline",
) -> List[Tuple[datetime, float]]:
    if horizon_minutes < 0:
        raise ValueError("horizon_minutes must be >= 0")
    if step_minutes <= 0:
        raise ValueError("step_minutes must be > 0")

    series: List[Tuple[datetime, float]] = []
    for offset in range(0, horizon_minutes + 1, step_minutes):
        dt = start_dt + timedelta(minutes=offset)
        if method == "baseline":
            y = baseline_stop_demand_forecast_per_hour(
                stop_id=stop_id,
                dt=dt,
                event_active=event_active,
                route_context_factor=route_context_factor,
            )
        elif method == "true":
            y = true_stop_demand_per_hour(
                stop_id=stop_id,
                dt=dt,
                event_active=event_active,
                route_context_factor=route_context_factor,
            )
        else:
            raise ValueError(f"unknown method: {method}")

        series.append((dt, y))
    return series


def build_demand_timeseries_dataframe(
    *,
    stops: Dict[str, str],
    start_dt: datetime,
    horizon_minutes: int,
    step_minutes: int,
    event_active: bool,
    route_context_factor: float = 1.0,
    method: Literal["baseline", "true"] = "baseline",
) -> pd.DataFrame:
    """
    Uzun form:
    timestamp, stop_id, stop_name, demand_per_hour
    """
    records: List[Dict[str, object]] = []
    for stop_id, stop_name in stops.items():
        series = predict_demand_series(
            stop_id=stop_id,
            start_dt=start_dt,
            horizon_minutes=horizon_minutes,
            step_minutes=step_minutes,
            event_active=event_active,
            route_context_factor=route_context_factor,
            method=method,
        )
        for ts, y in series:
            records.append(
                {
                    "timestamp": ts,
                    "stop_id": stop_id,
                    "stop_name": stop_name,
                    "demand_per_hour": y,
                }
            )
    return pd.DataFrame(records).sort_values(["stop_id", "timestamp"])


def evaluate_demand_model(
    *,
    route_context_factor: float = 1.0,
    event_active: bool = False,
    step_minutes: int = 60,
    horizon_minutes: int = 6 * 60,
) -> Dict[str, float]:
    """
    Demo backtesting:
    - true = daha keskin pikli ground truth
    - baseline = daha yumuşak zaman-serisi baseline
    """
    from datetime import timedelta as td

    stop_ids = sorted(_STOP_DEMAND_BIAS.keys())
    base_dt = datetime(2026, 1, 1, 0, 0, 0)

    preds: List[float] = []
    trues: List[float] = []

    for stop_id in stop_ids:
        for offset in range(0, horizon_minutes + 1, step_minutes):
            dt = base_dt + td(minutes=offset)
            trues.append(
                true_stop_demand_per_hour(
                    stop_id=stop_id,
                    dt=dt,
                    event_active=event_active,
                    route_context_factor=route_context_factor,
                )
            )
            preds.append(
                baseline_stop_demand_forecast_per_hour(
                    stop_id=stop_id,
                    dt=dt,
                    event_active=event_active,
                    route_context_factor=route_context_factor,
                )
            )

    y_true = np.array(trues, dtype=float)
    y_pred = np.array(preds, dtype=float)
    err = y_pred - y_true

    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    bias = float(np.mean(err))

    return {"mae": mae, "rmse": rmse, "bias": bias, "n": float(len(y_true))}

