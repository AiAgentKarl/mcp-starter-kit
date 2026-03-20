# MCP Server — Pre-Launch Checklist

Geh diese Liste durch, bevor du deinen Server veröffentlichst.

## Code-Qualität

- [ ] Alle Tools haben aussagekräftige Docstrings (was, parameter, rückgabe)
- [ ] Type-Hints auf allen Funktionsparametern
- [ ] Fehlerbehandlung in jedem Tool (try/except oder Validierung)
- [ ] Keine hardgecodeten API-Keys im Code
- [ ] API-Keys über Umgebungsvariablen / .env geladen
- [ ] Timeouts auf allen HTTP-Anfragen gesetzt
- [ ] Keine `print()` Statements (MCP nutzt stdio!)
- [ ] Rückgabewerte sind formatierte Strings (kein rohes JSON)

## Projekt-Struktur

- [ ] `pyproject.toml` hat korrekten `name` (PyPI-unique)
- [ ] `pyproject.toml` hat `[project.scripts]` Eintrag
- [ ] `pyproject.toml` hat `[tool.hatch.build.targets.wheel]` mit `packages`
- [ ] Alle `__init__.py` Dateien vorhanden
- [ ] `.gitignore` enthält `.env`, `__pycache__/`, `dist/`, `*.egg-info/`
- [ ] `README.md` vorhanden und vollständig

## README

- [ ] Server-Beschreibung (1-2 Sätze: was macht er?)
- [ ] Tool-Liste mit Beschreibungen
- [ ] Installation: `pip install your-server` / `uvx your-server`
- [ ] Konfiguration für Claude Desktop (JSON-Snippet)
- [ ] Konfiguration für Claude Code (.mcp.json Snippet)
- [ ] Benötigte API-Keys dokumentiert (welche, wo bekommt man sie)
- [ ] Beispiel-Ausgabe (was sieht der Agent?)
- [ ] Lizenz angegeben

## Testing

- [ ] `pip install -e .` funktioniert ohne Fehler
- [ ] Server startet: `your-server` zeigt keine Fehler
- [ ] MCP Inspector getestet: `npx @modelcontextprotocol/inspector your-server`
- [ ] Jedes Tool einzeln getestet
- [ ] Fehlerfälle getestet (ungültige Parameter, API down, etc.)
- [ ] Rate-Limits der APIs nicht überschritten

## PyPI-Veröffentlichung

- [ ] Version in `pyproject.toml` ist korrekt (Semantic Versioning)
- [ ] `python -m build` läuft ohne Fehler
- [ ] Paket auf Test-PyPI getestet: `pip install -i https://test.pypi.org/simple/ your-server`
- [ ] Auf echtes PyPI hochgeladen: `python -m twine upload dist/*`
- [ ] `pip install your-server && your-server` funktioniert

## GitHub Repository

- [ ] README.md im Repo-Root
- [ ] Lizenz-Datei (LICENSE) vorhanden
- [ ] `.gitignore` committed
- [ ] Keine Secrets im Repo (API-Keys, .env, etc.)
- [ ] GitHub Actions für automatisches Publishing (optional)

## Optional (Empfohlen)

- [ ] Smithery-Konfiguration (`smithery.yaml`) für smithery.ai
- [ ] Glama-Badge im README für glama.ai Indexierung
- [ ] Server im offiziellen MCP-Registry angemeldet
- [ ] Changelog begonnen (CHANGELOG.md)
- [ ] Beispiel-Screenshots oder Ausgabe im README
