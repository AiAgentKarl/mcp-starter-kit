"""
Multi-API MCP Server — Fortgeschrittenes Beispiel
===================================================

Kombiniert mehrere öffentliche APIs zu einem nützlichen Server:
- Open-Meteo: Wetterdaten (kostenlos, kein Key)
- RestCountries: Länderdaten (kostenlos, kein Key)
- Wikipedia: Zusammenfassungen (kostenlos, kein Key)

Zeigt fortgeschrittene Konzepte:
- Mehrere API-Clients mit unterschiedlichen Base-URLs
- Einfacher In-Memory-Cache mit TTL
- Daten aus mehreren APIs kombinieren
- Parallele API-Aufrufe mit asyncio.gather
- Robuste Fehlerbehandlung pro API
"""

import asyncio
import time
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# ============================================================
# Einfacher Cache
# ============================================================
# Verhindert unnötige API-Aufrufe bei wiederholten Anfragen

_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL = 300  # 5 Minuten


def _get_cached(key: str) -> Any | None:
    """Wert aus Cache holen, wenn nicht abgelaufen."""
    if key in _cache:
        timestamp, value = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return value
        del _cache[key]  # Abgelaufenen Eintrag entfernen
    return None


def _set_cached(key: str, value: Any) -> None:
    """Wert im Cache speichern."""
    _cache[key] = (time.time(), value)


# ============================================================
# Server
# ============================================================

mcp = FastMCP(
    name="multi-api-server",
    instructions=(
        "Kombiniert Wetter-, Länder- und Wikipedia-Daten. "
        "Kann Stadtprofile erstellen, Länder vergleichen und "
        "Reiseinformationen zusammenstellen."
    ),
)


# ============================================================
# API-Hilfsfunktionen
# ============================================================

async def _fetch_weather(lat: float, lon: float) -> dict[str, Any] | None:
    """Aktuelles Wetter von Open-Meteo abrufen."""
    cache_key = f"weather:{lat:.2f},{lon:.2f}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,wind_speed_10m,relative_humidity_2m,weather_code",
                    "timezone": "auto",
                },
            )
            response.raise_for_status()
            data = response.json()
            _set_cached(cache_key, data)
            return data
    except Exception:
        return None


async def _fetch_country(name: str) -> dict[str, Any] | None:
    """Länderdaten von RestCountries abrufen."""
    cache_key = f"country:{name.lower()}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"https://restcountries.com/v3.1/name/{name}",
                params={"fullText": "false"},
            )
            response.raise_for_status()
            data = response.json()
            if data:
                result = data[0]
                _set_cached(cache_key, result)
                return result
    except Exception:
        return None
    return None


async def _fetch_wikipedia(topic: str) -> str | None:
    """Wikipedia-Zusammenfassung abrufen."""
    cache_key = f"wiki:{topic.lower()}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}",
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            extract = data.get("extract", "")
            if extract:
                _set_cached(cache_key, extract)
            return extract or None
    except Exception:
        return None


# Wetter-Code in Text umwandeln
WEATHER_CODES = {
    0: "Klar", 1: "Überwiegend klar", 2: "Teilweise bewölkt",
    3: "Bewölkt", 45: "Nebel", 48: "Raureif-Nebel",
    51: "Leichter Nieselregen", 53: "Nieselregen", 55: "Starker Nieselregen",
    61: "Leichter Regen", 63: "Regen", 65: "Starker Regen",
    71: "Leichter Schnee", 73: "Schnee", 75: "Starker Schnee",
    80: "Regenschauer", 81: "Starke Regenschauer",
    95: "Gewitter", 96: "Gewitter mit Hagel",
}


# ============================================================
# Tools
# ============================================================

@mcp.tool()
async def get_country_profile(country: str) -> str:
    """
    Umfassendes Länderprofil erstellen.

    Kombiniert Länderdaten, aktuelle Wetterdaten der Hauptstadt
    und Wikipedia-Zusammenfassung.

    Args:
        country: Ländername (z.B. "Germany", "Japan", "Brazil")
    """
    # Alle drei APIs parallel aufrufen für Geschwindigkeit
    country_data, wiki_text = await asyncio.gather(
        _fetch_country(country),
        _fetch_wikipedia(country),
    )

    if not country_data:
        return f"Land '{country}' nicht gefunden. Bitte englischen Namen verwenden."

    # Grunddaten extrahieren
    name = country_data.get("name", {}).get("common", country)
    official = country_data.get("name", {}).get("official", "")
    capital_list = country_data.get("capital", [])
    capital = capital_list[0] if capital_list else "Unbekannt"
    population = country_data.get("population", 0)
    region = country_data.get("region", "Unbekannt")
    subregion = country_data.get("subregion", "")
    languages = country_data.get("languages", {})
    currencies = country_data.get("currencies", {})
    area = country_data.get("area", 0)
    latlng = country_data.get("capitalInfo", {}).get("latlng", [])

    # Wetter der Hauptstadt abrufen (wenn Koordinaten vorhanden)
    weather_data = None
    if latlng and len(latlng) >= 2:
        weather_data = await _fetch_weather(latlng[0], latlng[1])

    # Profil zusammenbauen
    lines = [
        f"=== {name} ===",
        f"Offizieller Name: {official}",
        f"Hauptstadt: {capital}",
        f"Region: {region}" + (f" / {subregion}" if subregion else ""),
        f"Bevölkerung: {population:,}".replace(",", "."),
        f"Fläche: {area:,.0f} km2".replace(",", "."),
    ]

    if languages:
        lang_str = ", ".join(languages.values())
        lines.append(f"Sprachen: {lang_str}")

    if currencies:
        curr_list = []
        for code, info in currencies.items():
            symbol = info.get("symbol", "")
            curr_name = info.get("name", code)
            curr_list.append(f"{curr_name} ({code}) {symbol}")
        lines.append(f"Währungen: {', '.join(curr_list)}")

    # Wetter
    if weather_data and "current" in weather_data:
        current = weather_data["current"]
        temp = current.get("temperature_2m", "?")
        wind = current.get("wind_speed_10m", "?")
        humidity = current.get("relative_humidity_2m", "?")
        code = current.get("weather_code", -1)
        weather_desc = WEATHER_CODES.get(code, "Unbekannt")

        lines.append("")
        lines.append(f"--- Aktuelles Wetter in {capital} ---")
        lines.append(f"Zustand: {weather_desc}")
        lines.append(f"Temperatur: {temp} C")
        lines.append(f"Wind: {wind} km/h")
        lines.append(f"Luftfeuchtigkeit: {humidity}%")

    # Wikipedia
    if wiki_text:
        # Auf 300 Zeichen kürzen
        short = wiki_text[:300]
        if len(wiki_text) > 300:
            short += "..."
        lines.append("")
        lines.append(f"--- Kurzinfo ---")
        lines.append(short)

    return "\n".join(lines)


@mcp.tool()
async def compare_countries(country_a: str, country_b: str) -> str:
    """
    Zwei Länder vergleichen.

    Stellt Bevölkerung, Fläche, Sprachen und Wetter gegenüber.

    Args:
        country_a: Erstes Land (z.B. "Germany")
        country_b: Zweites Land (z.B. "France")
    """
    # Beide Länder parallel laden
    data_a, data_b = await asyncio.gather(
        _fetch_country(country_a),
        _fetch_country(country_b),
    )

    if not data_a:
        return f"Land '{country_a}' nicht gefunden."
    if not data_b:
        return f"Land '{country_b}' nicht gefunden."

    name_a = data_a.get("name", {}).get("common", country_a)
    name_b = data_b.get("name", {}).get("common", country_b)

    pop_a = data_a.get("population", 0)
    pop_b = data_b.get("population", 0)
    area_a = data_a.get("area", 0)
    area_b = data_b.get("area", 0)

    def fmt(n: int | float) -> str:
        return f"{n:,.0f}".replace(",", ".")

    lines = [
        f"=== Vergleich: {name_a} vs. {name_b} ===",
        "",
        f"{'Merkmal':<20} {'| ' + name_a:<25} {'| ' + name_b:<25}",
        f"{'-' * 70}",
        f"{'Bevölkerung':<20} {'| ' + fmt(pop_a):<25} {'| ' + fmt(pop_b):<25}",
        f"{'Fläche (km2)':<20} {'| ' + fmt(area_a):<25} {'| ' + fmt(area_b):<25}",
    ]

    # Bevölkerungsdichte
    density_a = pop_a / area_a if area_a > 0 else 0
    density_b = pop_b / area_b if area_b > 0 else 0
    lines.append(
        f"{'Dichte (/km2)':<20} {'| ' + fmt(density_a):<25} {'| ' + fmt(density_b):<25}"
    )

    # Sprachen
    lang_a = ", ".join(data_a.get("languages", {}).values()) or "?"
    lang_b = ", ".join(data_b.get("languages", {}).values()) or "?"
    lines.append(f"{'Sprachen':<20} | {lang_a}")
    lines.append(f"{'':>20} | vs. {lang_b}")

    # Hauptstädte
    cap_a = (data_a.get("capital", ["?"]))[0] if data_a.get("capital") else "?"
    cap_b = (data_b.get("capital", ["?"]))[0] if data_b.get("capital") else "?"
    lines.append(
        f"{'Hauptstadt':<20} {'| ' + cap_a:<25} {'| ' + cap_b:<25}"
    )

    # Größenvergleich
    lines.append("")
    if pop_a > pop_b:
        factor = pop_a / pop_b if pop_b > 0 else 0
        lines.append(f"{name_a} hat {factor:.1f}x mehr Einwohner als {name_b}")
    elif pop_b > pop_a:
        factor = pop_b / pop_a if pop_a > 0 else 0
        lines.append(f"{name_b} hat {factor:.1f}x mehr Einwohner als {name_a}")

    return "\n".join(lines)


@mcp.tool()
async def get_topic_summary(topic: str) -> str:
    """
    Wikipedia-Zusammenfassung zu einem beliebigen Thema abrufen.

    Gibt eine kurze Zusammenfassung des Wikipedia-Artikels zurück.

    Args:
        topic: Thema oder Begriff (z.B. "Python programming language", "Berlin")
    """
    text = await _fetch_wikipedia(topic.replace(" ", "_"))

    if not text:
        return f"Kein Wikipedia-Artikel zu '{topic}' gefunden."

    return f"=== {topic} ===\n\n{text}"


def main():
    """Server starten."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
