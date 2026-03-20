"""
Konfiguration
=============

Lädt Umgebungsvariablen aus .env und stellt sie als Settings bereit.
API-Keys und andere Geheimnisse gehören IMMER in .env, nie in den Code.

Verwendung:
    from .config import settings
    api_key = settings.api_key
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# .env Datei laden (falls vorhanden)
load_dotenv()


@dataclass
class Settings:
    """
    Zentrale Einstellungen für den Server.

    Jede Einstellung wird aus der Umgebungsvariable geladen.
    Wenn keine gesetzt ist, wird der Standardwert verwendet.

    Beispiel .env Datei:
        API_KEY=dein-api-key-hier
        BASE_URL=https://api.example.com
        REQUEST_TIMEOUT=30
    """

    # API-Key für deinen Hauptdienst
    # Setze in .env: API_KEY=sk-...
    api_key: str = field(
        default_factory=lambda: os.getenv("API_KEY", "")
    )

    # Basis-URL der API
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "BASE_URL", "https://api.example.com"
        )
    )

    # Timeout für HTTP-Anfragen in Sekunden
    request_timeout: int = field(
        default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "30"))
    )

    # Cache-Dauer in Sekunden (0 = kein Cache)
    cache_ttl: int = field(
        default_factory=lambda: int(os.getenv("CACHE_TTL", "300"))
    )

    def validate(self) -> list[str]:
        """
        Prüft, ob alle nötigen Einstellungen gesetzt sind.
        Gibt eine Liste von Fehlern zurück (leer = alles ok).
        """
        errors = []
        if not self.api_key:
            errors.append("API_KEY ist nicht gesetzt (in .env oder Umgebung)")
        return errors


# Globale Settings-Instanz — importiere diese in anderen Modulen
settings = Settings()
