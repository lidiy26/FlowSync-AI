from __future__ import annotations

import hashlib
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple

import numpy as np


def _stable_noise(*parts: str) -> float:
    """
    Deterministik küçük gürültü üretir (runtime'a göre değişmez).
    """
    m = hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()
    v = int(m[:8], 16) / 0xFFFFFFFF  # 0..1
    return (v - 0.5) * 8.0  # -4..+4


def _peak_total(hour: float) -> float:
    """
    Sabah ve akşam piklerini temsil eden yumuşak (gauss) bileşenler.

    MVP demo'da doluluk dinamiğini yaklaşık olarak bu pike bağlarız.
    """
    morning = math.exp(-((hour - 8.0) / 2.2) ** 2)
    evening = 0.8 * math.exp(-((hour - 17.0) / 2.4) ** 2)
    return morning + evening


def predict_stop_occupancy_percent(
    *,
    stop_id: str,
    dt: datetime,
    event_active: bool,
    route_context_factor: float = 1.0,
    method: Literal["heuristic", "regression"] = "regression",
    noise_enabled: bool = True,
) -> float:
    """
    MVP demo için “1 saat öncesi tahmin” yerine, verilen `dt` anındaki durak
    doluluğunu deterministik bir modelle tahmin eder.

    - `method="heuristic"`: doğrudan kural tabanlı formül
    - `method="regression"`: aynı dinamiğin lineer regresyonla yakalanmış hali
    """
    if method == "heuristic":
        return _predict_stop_occupancy_heuristic(
            stop_id=stop_id,
            dt=dt,
            event_active=event_active,
            route_context_factor=route_context_factor,
            noise_enabled=noise_enabled,
        )
    if method == "regression":
        return _predict_stop_occupancy_regression(
            stop_id=stop_id,
            dt=dt,
            event_active=event_active,
            route_context_factor=route_context_factor,
            noise_enabled=noise_enabled,
        )

    raise ValueError(f"Bilinmeyen method: {method}")


_STOP_BIAS: Dict[str, float] = {
    "D1": -1.0,
    "D2": 6.0,
    "D3": 10.0,
    "D4": -3.0,
    "D5": 4.0,
    "D6": 6.0,
}

_EVENT_BONUS_PROFILE: Dict[str, float] = {
    "D2": 14.0,
    "D3": 18.0,
    "D5": 10.0,
}


def _hour_float(dt: datetime) -> float:
    return dt.hour + dt.minute / 60.0


def _predict_stop_occupancy_no_noise(
    *,
    stop_id: str,
    dt: datetime,
    event_active: bool,
    route_context_factor: float,
) -> float:
    hour = _hour_float(dt)
    peak = _peak_total(hour)

    # Saat bazlı trafik yoğunluğu (kabaca 30..90 arası) * route bağlamı.
    base = 30.0 + 60.0 * peak

    stop_bias = _STOP_BIAS.get(stop_id, 0.0)
    event_bonus = _EVENT_BONUS_PROFILE.get(stop_id, 0.0) if event_active else 0.0

    return (base * route_context_factor) + stop_bias + event_bonus


def _predict_stop_occupancy_heuristic(
    *,
    stop_id: str,
    dt: datetime,
    event_active: bool,
    route_context_factor: float,
    noise_enabled: bool,
) -> float:
    occupancy = _predict_stop_occupancy_no_noise(
        stop_id=stop_id,
        dt=dt,
        event_active=event_active,
        route_context_factor=route_context_factor,
    )

    if noise_enabled:
        noise = _stable_noise(stop_id, str(event_active), dt.isoformat())
        occupancy += noise

    # MVP demo için güvenli aralık.
    return max(5.0, min(98.0, float(occupancy)))


@dataclass(frozen=True)
class _LinearRegressionModel:
    # features: [const, route_factor, route_factor_peak_total, stop_bias, event_bonus_active]
    weights: np.ndarray  # shape: (5,)

    def predict_no_noise(
        self,
        *,
        stop_id: str,
        dt: datetime,
        event_active: bool,
        route_context_factor: float,
    ) -> float:
        hour = _hour_float(dt)
        peak_total = _peak_total(hour)

        route_factor = float(route_context_factor)
        route_factor_peak_total = route_factor * float(peak_total)
        stop_bias = float(_STOP_BIAS.get(stop_id, 0.0))
        event_bonus_active = float(_EVENT_BONUS_PROFILE.get(stop_id, 0.0)) if event_active else 0.0

        x = np.array(
            [
                1.0,
                route_factor,
                route_factor_peak_total,
                stop_bias,
                event_bonus_active,
            ],
            dtype=float,
        )
        return float(x @ self.weights)


_REGRESSION_MODEL: _LinearRegressionModel | None = None


def _fit_regression_model() -> _LinearRegressionModel:
    # Synthetic veri ile baseline regresyonu “eğitiyoruz”.
    # Bu MVP’de gerçek bilet/görüntü verisi olmadığı için dinamiği
    # formülün kendisinden türetiyoruz (debug ve doğrulama amaçlı).
    rng = np.random.default_rng(42)
    stop_ids = sorted(_STOP_BIAS.keys())
    route_factors = [0.92, 0.97, 1.0, 1.05, 1.12]
    hours = list(range(0, 24, 2))

    rows: List[np.ndarray] = []
    ys: List[float] = []

    # En küçük kapsam ama deterministik yeterlilik.
    base_dt = datetime(2026, 1, 1, 0, 0, 0)

    for stop_id in stop_ids:
        for event_active in [False, True]:
            for hour in hours:
                for rf in route_factors:
                    dt = base_dt.replace(hour=int(hour), minute=int(rng.integers(0, 60)))
                    y = _predict_stop_occupancy_no_noise(
                        stop_id=stop_id,
                        dt=dt,
                        event_active=event_active,
                        route_context_factor=rf,
                    )

                    peak_total = _peak_total(_hour_float(dt))
                    x = np.array(
                        [
                            1.0,
                            float(rf),
                            float(rf * peak_total),
                            float(_STOP_BIAS.get(stop_id, 0.0)),
                            float(_EVENT_BONUS_PROFILE.get(stop_id, 0.0)) if event_active else 0.0,
                        ],
                        dtype=float,
                    )
                    rows.append(x)
                    ys.append(float(y))

    X = np.vstack(rows)  # (N,5)
    y_vec = np.array(ys, dtype=float)  # (N,)

    # Least squares fit.
    weights, *_ = np.linalg.lstsq(X, y_vec, rcond=None)
    return _LinearRegressionModel(weights=weights)


def _get_regression_model() -> _LinearRegressionModel:
    global _REGRESSION_MODEL
    if _REGRESSION_MODEL is None:
        _REGRESSION_MODEL = _fit_regression_model()
    return _REGRESSION_MODEL


def _predict_stop_occupancy_regression(
    *,
    stop_id: str,
    dt: datetime,
    event_active: bool,
    route_context_factor: float,
    noise_enabled: bool,
) -> float:
    model = _get_regression_model()
    occupancy = model.predict_no_noise(
        stop_id=stop_id,
        dt=dt,
        event_active=event_active,
        route_context_factor=route_context_factor,
    )

    if noise_enabled:
        noise = _stable_noise(stop_id, str(event_active), dt.isoformat())
        occupancy += noise

    return max(5.0, min(98.0, float(occupancy)))


def predict_stop_occupancy_series(
    *,
    stop_id: str,
    start_dt: datetime,
    horizon_minutes: int,
    step_minutes: int,
    event_active: bool,
    route_context_factor: float = 1.0,
    method: Literal["heuristic", "regression"] = "regression",
) -> List[Tuple[datetime, float]]:
    if horizon_minutes < 0:
        raise ValueError("horizon_minutes must be >= 0")
    if step_minutes <= 0:
        raise ValueError("step_minutes must be > 0")
    from datetime import timedelta

    points: List[Tuple[datetime, float]] = []
    for offset in range(0, horizon_minutes + 1, step_minutes):
        dt = start_dt + timedelta(minutes=offset)
        occ = predict_stop_occupancy_percent(
            stop_id=stop_id,
            dt=dt,
            event_active=event_active,
            route_context_factor=route_context_factor,
            method=method,
            noise_enabled=False,
        )
        points.append((dt, occ))

    return points


def build_occupancy_timeseries_dataframe(
    *,
    stops: Dict[str, str],
    start_dt: datetime,
    horizon_minutes: int,
    step_minutes: int,
    event_active: bool,
    route_context_factor: float = 1.0,
    method: Literal["heuristic", "regression"] = "regression",
) -> "pd.DataFrame":
    """
    Uzun form time series: stop_id, stop_name, timestamp, occupancy_percent
    """
    import pandas as pd

    records = []
    for stop_id, stop_name in stops.items():
        series = predict_stop_occupancy_series(
            stop_id=stop_id,
            start_dt=start_dt,
            horizon_minutes=horizon_minutes,
            step_minutes=step_minutes,
            event_active=event_active,
            route_context_factor=route_context_factor,
            method=method,
        )
        for ts, occ in series:
            records.append(
                {
                    "timestamp": ts,
                    "stop_id": stop_id,
                    "stop_name": stop_name,
                    "occupancy_percent": occ,
                }
            )
    return pd.DataFrame(records).sort_values(["stop_id", "timestamp"])


def evaluate_occupancy_model(
    *,
    method: Literal["heuristic", "regression"] = "regression",
    route_context_factor: float = 1.0,
    event_active: bool | None = None,
    step_minutes: int = 60,
    horizon_minutes: int = 24 * 60,
) -> Dict[str, float]:
    """
    Demo kalibrasyonu için:
    - “ground truth” = noise'suz (formül) occupancy
    - “prediction” = seçilen method (noise'suz)
    """
    if step_minutes <= 0:
        raise ValueError("step_minutes must be > 0")
    if horizon_minutes <= 0:
        raise ValueError("horizon_minutes must be > 0")

    from datetime import timedelta

    stop_ids = sorted(_STOP_BIAS.keys())
    base_dt = datetime(2026, 1, 1, 0, 0, 0)

    preds: List[float] = []
    trues: List[float] = []

    for stop_id in stop_ids:
        for offset in range(0, horizon_minutes + 1, step_minutes):
            dt = base_dt + timedelta(minutes=offset)
            for ev in ([event_active] if event_active is not None else [False, True]):
                true_y = _predict_stop_occupancy_no_noise(
                    stop_id=stop_id,
                    dt=dt,
                    event_active=bool(ev),
                    route_context_factor=route_context_factor,
                )
                pred_y = predict_stop_occupancy_percent(
                    stop_id=stop_id,
                    dt=dt,
                    event_active=bool(ev),
                    route_context_factor=route_context_factor,
                    method=method,
                    noise_enabled=False,
                )
                trues.append(true_y)
                preds.append(pred_y)

    y_true = np.array(trues, dtype=float)
    y_pred = np.array(preds, dtype=float)
    err = y_pred - y_true

    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    bias = float(np.mean(err))

    return {
        "mae": mae,
        "rmse": rmse,
        "bias": bias,
        "n": float(len(y_true)),
    }


def estimate_occupancy_uncertainty_percent(
    *,
    stop_id: str,
    dt: datetime,
    event_active: bool,
    route_context_factor: float = 1.0,
) -> float:
    """
    MVP belirsizlik proxy'si:
    - heuristic vs regression farkı (noise'suz)
    - ölçü: mutlak farkın ölçeklenmiş hali
    """
    y_h = predict_stop_occupancy_percent(
        stop_id=stop_id,
        dt=dt,
        event_active=event_active,
        route_context_factor=route_context_factor,
        method="heuristic",
        noise_enabled=False,
    )
    y_r = predict_stop_occupancy_percent(
        stop_id=stop_id,
        dt=dt,
        event_active=event_active,
        route_context_factor=route_context_factor,
        method="regression",
        noise_enabled=False,
    )
    return float(min(20.0, abs(y_h - y_r)))

