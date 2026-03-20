"""
Beispiel API-Client
====================

Async HTTP-Client für eine externe API.
Nutzt httpx für non-blocking Requests.

Jede API bekommt ihren eigenen Client in einer eigenen Datei.
So bleibt der Code übersichtlich und testbar.

Verwendung:
    async with ExampleClient() as client:
        result = await client.search("query")

Tipps:
- Immer `async with` verwenden (schließt die Verbindung sauber)
- Timeouts setzen (nie endlos warten)
- Fehler abfangen und verständliche Meldungen zurückgeben
- Rate-Limits der API beachten
"""

from typing import Any

import httpx

from ..config import settings


class ExampleClient:
    """
    HTTP-Client für die Example-API.

    Verwaltet die Verbindung, Authentication und Fehlerbehandlung.
    """

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "ExampleClient":
        """Verbindung öffnen (für `async with`)."""
        self._client = httpx.AsyncClient(
            base_url=settings.base_url,
            timeout=settings.request_timeout,
            headers={
                # API-Key im Header mitsenden (häufigste Methode)
                "Authorization": f"Bearer {settings.api_key}",
                "Accept": "application/json",
            },
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Verbindung schließen."""
        if self._client:
            await self._client.aclose()

    async def search(
        self, query: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Nach Items suchen.

        Args:
            query: Suchbegriff
            limit: Max. Ergebnisse

        Returns:
            Liste von Item-Dictionaries
        """
        assert self._client is not None, "Client nicht initialisiert (async with nutzen)"

        response = await self._client.get(
            "/search",
            params={"q": query, "limit": limit},
        )
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        """
        Ein Item anhand seiner ID abrufen.

        Args:
            item_id: Die eindeutige Item-ID

        Returns:
            Item-Dictionary oder None wenn nicht gefunden
        """
        assert self._client is not None, "Client nicht initialisiert (async with nutzen)"

        response = await self._client.get(f"/items/{item_id}")

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()
