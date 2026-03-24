from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .route_optimizer import RouteOption, pick_main_and_fastest


@dataclass(frozen=True)
class NudgingDecision:
    applies: bool
    discount_percent: int
    message: str
    recommended_route: Optional[RouteOption]
    fastest_route: Optional[RouteOption]


def get_nudging_decision(
    routes: list[RouteOption],
    *,
    high_crowding_threshold_percent: float,
    discount_percent: int,
    time_sensitive: bool = False,
) -> NudgingDecision:
    main_route, fastest_route = pick_main_and_fastest(routes)

    if main_route is None or fastest_route is None:
        return NudgingDecision(
            applies=False,
            discount_percent=discount_percent,
            message="",
            recommended_route=main_route,
            fastest_route=fastest_route,
        )

    # Nudging mantığı:
    # - “en hızlı” rota kalabalık ise
    # - konfor açısından “ana rota” belirgin biçimde daha iyi ise
    # alternatif öner.
    fastest_crowd = fastest_route.avg_occupancy_percent
    main_crowd = main_route.avg_occupancy_percent
    crowd_improvement = fastest_crowd - main_crowd

    extra_time = main_route.total_time_minutes - fastest_route.total_time_minutes
    extra_time_ok = extra_time <= 8.0  # konforu bozmayacak süre eşiği

    # Fairness (adalet) MVP kuralı:
    # - “zaman duyarlı” kullanıcılar için, sadece doluluk kazancı belirgin değilse
    #   zaman kaybı yüksek yönlendirme yapma.
    if time_sensitive:
        should_apply = (
            fastest_crowd >= high_crowding_threshold_percent
            and (
                (crowd_improvement >= 18.0 and extra_time_ok)
                or (crowd_improvement >= 28.0)  # çok büyük doluluk kazancı varsa tolere et
            )
        )
    else:
        should_apply = (
            fastest_crowd >= high_crowding_threshold_percent
            and crowd_improvement >= 15.0
        )

    if should_apply:
        extra_time_txt = f"+{extra_time:.0f} dk" if extra_time > 0 else "aynı süre"
        message = (
            f"Bu otobüse binerseniz {discount_percent}% indirim kazanacaksınız! "
            f"Öngörüde “{fastest_route.route_name}” hattında ortalama doluluk yüksek. "
            f"Daha konforlu seçenek: “{main_route.route_name}” ({crowd_improvement:.0f}% daha düşük doluluk, {extra_time_txt})."
        )
        return NudgingDecision(
            applies=True,
            discount_percent=discount_percent,
            message=message,
            recommended_route=main_route,
            fastest_route=fastest_route,
        )

    return NudgingDecision(
        applies=False,
        discount_percent=discount_percent,
        message="",
        recommended_route=main_route,
        fastest_route=fastest_route,
    )

