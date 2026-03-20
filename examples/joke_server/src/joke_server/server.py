"""
Joke MCP Server — Einsteiger-Beispiel
======================================

Ein minimaler MCP-Server der Witze von der JokeAPI abruft.
Zeigt die Grundlagen: Server erstellen, Tool definieren, API aufrufen.

API: https://v2.jokeapi.dev/ (kostenlos, kein Key nötig)
"""

import httpx
from mcp.server.fastmcp import FastMCP

# Server erstellen
mcp = FastMCP(
    name="joke-server",
    instructions="Liefert zufällige Witze aus verschiedenen Kategorien.",
)

# Verfügbare Kategorien
CATEGORIES = ["Programming", "Misc", "Dark", "Pun", "Spooky", "Christmas"]


@mcp.tool()
async def get_joke(category: str = "Any") -> str:
    """
    Einen zufälligen Witz abrufen.

    Liefert einen Witz aus der gewählten Kategorie.
    Unterstützt: Programming, Misc, Dark, Pun, Spooky, Christmas, oder Any für alle.

    Args:
        category: Witz-Kategorie (Standard: "Any" für zufällig)
    """
    # Kategorie validieren
    if category != "Any" and category not in CATEGORIES:
        return (
            f"Unbekannte Kategorie '{category}'. "
            f"Verfügbar: {', '.join(CATEGORIES)} oder 'Any'"
        )

    # API aufrufen
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"https://v2.jokeapi.dev/joke/{category}",
            params={"type": "twopart"},  # Nur Witze mit Setup + Punchline
        )
        response.raise_for_status()
        data = response.json()

    # Fehler prüfen
    if data.get("error"):
        return f"API-Fehler: {data.get('message', 'Unbekannter Fehler')}"

    # Witz formatieren
    return (
        f"Kategorie: {data['category']}\n\n"
        f"{data['setup']}\n"
        f"... {data['delivery']}"
    )


@mcp.tool()
async def get_categories() -> str:
    """
    Verfügbare Witz-Kategorien auflisten.

    Gibt alle Kategorien zurück, die für get_joke verwendet werden können.
    """
    lines = ["Verfügbare Kategorien:"]
    for cat in CATEGORIES:
        lines.append(f"  - {cat}")
    lines.append("")
    lines.append("Nutze 'Any' für eine zufällige Kategorie.")
    return "\n".join(lines)


def main():
    """Server starten."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
