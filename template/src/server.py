"""
MCP Server — Hauptdatei
=======================

Hier wird der FastMCP-Server erstellt und alle Tools registriert.
Starte den Server mit: `your-mcp-server` (nach pip install -e .)

Architektur:
- server.py      → Erstellt den Server, registriert Tools
- config.py      → Lädt Umgebungsvariablen und Einstellungen
- tools/         → Jede Datei enthält eine Gruppe von Tools
- clients/       → HTTP-Clients für externe APIs
"""

from mcp.server.fastmcp import FastMCP

# Tools importieren
from .tools.example import register_tools

# ============================================================
# Server erstellen
# ============================================================
# `name` erscheint in der Tool-Liste des AI-Agents
# `instructions` erklärt dem Agent, was der Server kann
mcp = FastMCP(
    name="your-mcp-server",
    instructions=(
        "Beschreibe hier, was dein Server macht. "
        "Diese Beschreibung hilft dem AI-Agent zu verstehen, "
        "wann er deine Tools verwenden soll."
    ),
)

# ============================================================
# Tools registrieren
# ============================================================
# Jedes Tool-Modul hat eine register_tools(mcp) Funktion
register_tools(mcp)

# Tipp: Für weitere Tool-Gruppen einfach neue Module erstellen:
# from .tools.another_group import register_tools as register_another
# register_another(mcp)


def main():
    """Server starten (wird von pyproject.toml [project.scripts] aufgerufen)."""
    # stdio = Standard-Transport, funktioniert mit allen MCP-Clients
    # Alternativen: "sse" für Server-Sent Events, "streamable-http"
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
