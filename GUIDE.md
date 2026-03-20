# MCP Server — Step-by-Step Guide

## Was ist MCP?

Das Model Context Protocol (MCP) ist ein offener Standard, der AI-Agents (Claude, GPT, etc.) ermöglicht, externe Tools und Daten zu nutzen. Dein MCP-Server stellt Tools bereit, die ein Agent aufrufen kann.

**Beispiel:** Ein Agent fragt "Wie ist das Wetter in Berlin?" → Dein Server hat ein `get_weather("Berlin")` Tool → Agent ruft es auf → Bekommt die Antwort.

---

## Phase 1: Setup (5 Minuten)

### 1.1 Template kopieren

```bash
cp -r template/ mein-server/
cd mein-server/
```

### 1.2 Projekt umbenennen

In `pyproject.toml` diese Platzhalter ersetzen:

| Platzhalter | Ersetzen mit | Beispiel |
|---|---|---|
| `your-mcp-server` | Dein Paketname (mit Bindestrichen) | `weather-mcp-server` |
| `your_mcp_server` | Python-Paketname (mit Unterstrichen) | `weather_mcp_server` |
| `Your Name` | Dein Name | `Max Mustermann` |
| `your-github-username` | GitHub Username | `maxmuster` |

**WICHTIG:** Der Ordner `src/your_mcp_server/` muss auch umbenannt werden!

```bash
mv src/your_mcp_server/ src/weather_mcp_server/
```

### 1.3 Abhängigkeiten installieren

```bash
pip install -e .
```

Das installiert deinen Server im Entwicklungsmodus. Änderungen am Code werden sofort wirksam.

---

## Phase 2: Dein erstes Tool (10 Minuten)

### 2.1 Aufbau verstehen

Ein MCP-Tool besteht aus:
- **Funktion** — Async Python-Funktion
- **Decorator** — `@mcp.tool()` registriert sie als Tool
- **Docstring** — Beschreibung für den Agent (WICHTIG!)
- **Type Hints** — Parameter-Typen (Agent sieht diese)

### 2.2 Ein einfaches Tool schreiben

Öffne `src/tools/example.py` und ersetze den Inhalt:

```python
from mcp.server.fastmcp import FastMCP
import httpx


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_weather(city: str) -> str:
        """
        Aktuelles Wetter einer Stadt abfragen.

        Gibt Temperatur, Windgeschwindigkeit und Zustand zurück.

        Args:
            city: Name der Stadt (z.B. "Berlin", "New York")
        """
        # Koordinaten der Stadt ermitteln (Geocoding)
        async with httpx.AsyncClient(timeout=10) as client:
            geo = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1},
            )
            geo.raise_for_status()
            results = geo.json().get("results", [])

            if not results:
                return f"Stadt '{city}' nicht gefunden."

            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            name = results[0]["name"]

            # Wetter abrufen
            weather = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,wind_speed_10m",
                },
            )
            weather.raise_for_status()
            current = weather.json()["current"]

        return (
            f"Wetter in {name}:\n"
            f"Temperatur: {current['temperature_2m']} C\n"
            f"Wind: {current['wind_speed_10m']} km/h"
        )
```

### 2.3 Rückgabewerte

Tools geben **immer Strings** zurück. Der Agent liest diese und interpretiert sie.

Tipps:
- Formatiere übersichtlich mit Zeilenumbrüchen
- Nutze Überschriften und Trennlinien für komplexe Daten
- Keine JSON zurückgeben (Strings sind für Agents besser lesbar)

---

## Phase 3: Testen (5 Minuten)

### 3.1 Mit MCP Inspector testen

```bash
npx @modelcontextprotocol/inspector your-mcp-server
```

Öffnet eine Web-UI wo du deine Tools einzeln aufrufen und die Ergebnisse sehen kannst.

### 3.2 Mit Claude Code testen

Erstelle eine `.mcp.json` im Projektordner:

```json
{
    "mcpServers": {
        "your-mcp-server": {
            "command": "uv",
            "args": ["run", "--with", ".", "your-mcp-server"]
        }
    }
}
```

Dann öffne Claude Code im Projektordner — dein Server wird automatisch geladen.

### 3.3 Häufige Fehler

| Problem | Ursache | Lösung |
|---|---|---|
| "Module not found" | Package-Name stimmt nicht | `pyproject.toml` [tool.hatch.build.targets.wheel] prüfen |
| "No tools found" | Tools nicht registriert | `register_tools()` in `server.py` aufrufen |
| Tool gibt Fehler | API nicht erreichbar | Timeout und Fehlerbehandlung ergänzen |
| Server startet nicht | Syntax-Fehler | `python -c "from your_package.server import main"` testen |

---

## Phase 4: Weitere Tools hinzufügen

### 4.1 Neue Tool-Gruppe erstellen

Erstelle eine neue Datei `src/tools/analysis.py`:

```python
from mcp.server.fastmcp import FastMCP

def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def analyze_data(dataset: str) -> str:
        """Daten analysieren..."""
        # Deine Logik
        return "Ergebnis"
```

### 4.2 In Server registrieren

In `server.py` hinzufügen:

```python
from .tools.analysis import register_tools as register_analysis
register_analysis(mcp)
```

### 4.3 Best Practices

- **Ein Tool = Eine Aufgabe:** `get_weather` statt `get_weather_and_forecast_and_alerts`
- **Klare Parameter:** `city: str` statt `input: str`
- **Gute Docstrings:** Der Agent entscheidet anhand des Docstrings, welches Tool er nutzt
- **Fehlerbehandlung:** Immer lesbare Fehlermeldungen zurückgeben
- **Rate-Limits beachten:** Cache nutzen, nicht die API fluten

---

## Phase 5: Auf PyPI veröffentlichen

### 5.1 Build-Tools installieren

```bash
pip install build twine
```

### 5.2 Paket bauen

```bash
python -m build
```

Erstellt `dist/your-mcp-server-0.1.0.tar.gz` und `.whl`.

### 5.3 Auf PyPI hochladen

```bash
# Erst auf Test-PyPI probieren (optional aber empfohlen)
python -m twine upload --repository testpypi dist/*

# Dann auf echtes PyPI
python -m twine upload dist/*
```

Du brauchst einen PyPI-Account und API-Token: https://pypi.org/manage/account/token/

### 5.4 Testen, ob es funktioniert

```bash
pip install your-mcp-server
your-mcp-server  # Sollte ohne Fehler starten
```

---

## Phase 6: README für PyPI schreiben

Dein README sollte enthalten:

1. **Was macht der Server?** (1-2 Sätze)
2. **Verfügbare Tools** (Liste mit Beschreibungen)
3. **Installation** (`pip install ...`)
4. **Konfiguration** (Claude Desktop, Claude Code, etc.)
5. **Beispiel-Ausgabe** (Was sieht der Agent?)
6. **Benötigte API-Keys** (falls vorhanden)

Beispiel für die Konfigurationssektion:

```markdown
### Claude Desktop

Füge zu `claude_desktop_config.json` hinzu:

\```json
{
  "mcpServers": {
    "your-server": {
      "command": "uvx",
      "args": ["your-mcp-server"]
    }
  }
}
\```
```

---

## Nächste Schritte

- Schau dir die 3 Beispiele in `examples/` an (steigender Schwierigkeitsgrad)
- Nutze die `CHECKLIST.md` vor dem Veröffentlichen
- Melde deinen Server im MCP-Registry an: https://github.com/modelcontextprotocol/servers
