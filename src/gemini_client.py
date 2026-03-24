from __future__ import annotations

import os
from typing import List

import streamlit as st

from .route_optimizer import RouteOption
from .nudging import NudgingDecision


def _get_google_api_key() -> str | None:
    # Streamlit secrets (tercih)
    try:
        if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
            key = st.secrets.get("GOOGLE_API_KEY")
            if key:
                return str(key)
    except Exception:
        # st.secrets kullanımında sorun olsa bile env fallback'e geç.
        pass

    # Ortam değişkeni fallback
    key = os.environ.get("GOOGLE_API_KEY")
    return key if key else None


def _fallback_explanation(*, routes: List[RouteOption], nudging: NudgingDecision) -> str:
    if not routes:
        return "Bu demo için uygun rota bulunamadı."

    recommended = nudging.recommended_route or routes[0]
    fastest = nudging.fastest_route or routes[0]

    parts = [
        f"Önerim: “{recommended.route_name}” hattı (beklenen ortalama doluluk: {recommended.avg_occupancy_percent:.0f}%).",
        f"Karşılaştırma: En hızlı seçenek “{fastest.route_name}” ({fastest.total_time_minutes:.0f} dk) ama doluluk daha yüksek olabilir ({fastest.avg_occupancy_percent:.0f}%).",
    ]
    if nudging.applies:
        parts.append(
            f"Yoğunluk yüksek olduğu için “{recommended.route_name}” seçersen {nudging.discount_percent}% indirim kazanırsın."
        )
    return " ".join(parts)


def generate_ai_explanation(
    *,
    origin_name: str,
    destination_name: str,
    departure_label: str,
    routes: List[RouteOption],
    nudging: NudgingDecision,
) -> str:
    """
    Gemini tabanlı açıklama üretir. API anahtarı yoksa heuristik fallback döner.
    """
    key = _get_google_api_key()
    if not key:
        return _fallback_explanation(routes=routes, nudging=nudging)

    try:
        import google.generativeai as genai

        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-pro")

        route_lines = []
        for r in routes:
            route_lines.append(
                f"- {r.route_name}: {r.total_time_minutes:.0f} dk, ort. doluluk {r.avg_occupancy_percent:.0f}%, max {r.max_occupancy_percent:.0f}%"
            )

        prompt = f"""
Sen bir toplu taşıma optimizasyon asistanısın.

Aşağıdaki verilere göre kullanıcıya (Türkçe) 4-6 cümlelik, anlaşılır bir açıklama yaz.
Ton: nazik ve bilgilendirici.
İçerik: neden bu rotayı öneriyorsun, yoğunluk durumunu nasıl yorumluyorsun, nudging varsa neden/sonuç.

Kullanıcı bilgisi:
- Başlangıç: {origin_name}
- Varış: {destination_name}
- Kalkış: {departure_label}

Rota seçenekleri:
{chr(10).join(route_lines)}

Nudging durumu:
- Uygulanıyor mu: {str(nudging.applies)}
- Mesaj: {nudging.message}

Kısıtlar:
- Kesin sayılar dışında “yaklaşık” ve “öngörü” ifadeleri kullan.
- Veri uydurma: sadece verilen sayıları kullan, başka varsayım ekleme.
""".strip()

        resp = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2, "max_output_tokens": 300},
        )

        text = getattr(resp, "text", None) or ""
        text = text.strip()
        if not text:
            return _fallback_explanation(routes=routes, nudging=nudging)
        return text
    except Exception as e:
        # UI'de dostça hata göstermek için fallback dönüyoruz.
        return (
            _fallback_explanation(routes=routes, nudging=nudging)
            + f"\n\n(Not: Gemini açıklaması üretilemedi: {type(e).__name__})"
        )

