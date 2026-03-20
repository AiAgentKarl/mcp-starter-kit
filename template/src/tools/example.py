"""
Beispiel-Tools
==============

Hier definierst du deine MCP-Tools. Jedes Tool ist eine async Funktion
mit einem @mcp.tool() Decorator.

WICHTIG: Der Docstring der Funktion wird dem AI-Agent als Beschreibung
angezeigt. Schreib ihn so, dass ein Agent versteht:
1. Was das Tool macht
2. Welche Parameter es braucht
3. Was es zurückgibt

Tipps:
- Ein Tool pro Aufgabe (nicht zu viel in ein Tool packen)
- Klare Parameter-Namen und Typen
- Aussagekräftige Fehlermeldungen
- Rückgabe als formatierter String (nicht JSON)
"""

from mcp.server.fastmcp import FastMCP

# Client für API-Aufrufe importieren
from ..clients.example_client import ExampleClient


def register_tools(mcp: FastMCP) -> None:
    """Registriert alle Tools dieser Gruppe am Server."""

    # ==============================================================
    # Tool 1: Einfaches Tool ohne Parameter
    # ==============================================================
    @mcp.tool()
    async def get_status() -> str:
        """
        Server-Status abfragen.

        Gibt den aktuellen Status des Servers und der API-Verbindung zurück.
        Nützlich um zu prüfen, ob alles funktioniert.
        """
        # Hier kommt deine Logik hin
        return "Server läuft. API-Verbindung: OK"

    # ==============================================================
    # Tool 2: Tool mit Parametern
    # ==============================================================
    @mcp.tool()
    async def search_items(
        query: str,
        limit: int = 10,
    ) -> str:
        """
        Nach Items suchen.

        Durchsucht die Datenbank nach Items die zum Suchbegriff passen.

        Args:
            query: Suchbegriff (z.B. "Python", "Machine Learning")
            limit: Maximale Anzahl Ergebnisse (Standard: 10, Max: 50)
        """
        # Parameter validieren
        if not query.strip():
            return "Fehler: Suchbegriff darf nicht leer sein."
        limit = min(limit, 50)  # Maximum begrenzen

        # API aufrufen
        async with ExampleClient() as client:
            results = await client.search(query=query, limit=limit)

        # Ergebnisse formatieren
        if not results:
            return f"Keine Ergebnisse für '{query}' gefunden."

        lines = [f"Suchergebnisse für '{query}' ({len(results)} Treffer):"]
        lines.append("")
        for i, item in enumerate(results, 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   Beschreibung: {item.get('description', 'Keine')}")
            lines.append("")

        return "\n".join(lines)

    # ==============================================================
    # Tool 3: Tool mit Fehlerbehandlung
    # ==============================================================
    @mcp.tool()
    async def get_item_details(item_id: str) -> str:
        """
        Details zu einem bestimmten Item abrufen.

        Args:
            item_id: Die eindeutige ID des Items (z.B. "abc123")
        """
        if not item_id.strip():
            return "Fehler: Item-ID darf nicht leer sein."

        try:
            async with ExampleClient() as client:
                item = await client.get_by_id(item_id)

            if not item:
                return f"Item mit ID '{item_id}' nicht gefunden."

            # Formatierte Ausgabe
            return (
                f"Item: {item['title']}\n"
                f"ID: {item['id']}\n"
                f"Status: {item.get('status', 'Unbekannt')}\n"
                f"Erstellt: {item.get('created_at', 'Unbekannt')}\n"
                f"Beschreibung: {item.get('description', 'Keine')}"
            )

        except Exception as e:
            return f"Fehler beim Abrufen von Item '{item_id}': {e}"
