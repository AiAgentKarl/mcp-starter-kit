"""
GitHub MCP Server — Mittelstufe-Beispiel
=========================================

MCP-Server der GitHub-Daten abfragt: Repos, Issues, Benutzerprofile.
Zeigt: Authentication, Fehlerbehandlung, mehrere Tools, Paginierung.

API: https://docs.github.com/en/rest
Benötigt: GITHUB_TOKEN in .env (optional, erhöht Rate-Limit von 60 auf 5000/h)
"""

import os
from datetime import datetime

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Server erstellen
mcp = FastMCP(
    name="github-server",
    instructions=(
        "GitHub-Daten abfragen: Repositories, Issues, Benutzerprofile und Stars. "
        "Nützlich für Code-Recherche und Projekt-Analyse."
    ),
)

# GitHub API Konfiguration
BASE_URL = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "")


def _get_headers() -> dict[str, str]:
    """HTTP-Headers für GitHub API zusammenbauen."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "github-mcp-server/0.1.0",
    }
    # Token ist optional, erhöht aber das Rate-Limit erheblich
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


def _format_number(n: int) -> str:
    """Große Zahlen formatieren (z.B. 1500 → '1.5k')."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _format_date(iso_date: str | None) -> str:
    """ISO-Datum in lesbares Format umwandeln."""
    if not iso_date:
        return "Unbekannt"
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, AttributeError):
        return iso_date


@mcp.tool()
async def get_repo_info(owner: str, repo: str) -> str:
    """
    Informationen zu einem GitHub-Repository abrufen.

    Gibt Details wie Stars, Forks, Sprache und Beschreibung zurück.

    Args:
        owner: Repository-Besitzer (z.B. "facebook")
        repo: Repository-Name (z.B. "react")
    """
    async with httpx.AsyncClient(
        base_url=BASE_URL, headers=_get_headers(), timeout=15
    ) as client:
        response = await client.get(f"/repos/{owner}/{repo}")

        if response.status_code == 404:
            return f"Repository '{owner}/{repo}' nicht gefunden."
        if response.status_code == 403:
            return "Rate-Limit erreicht. Setze GITHUB_TOKEN in .env für mehr Anfragen."
        response.raise_for_status()

        data = response.json()

    return (
        f"Repository: {data['full_name']}\n"
        f"Beschreibung: {data.get('description', 'Keine')}\n"
        f"Sprache: {data.get('language', 'Keine')}\n"
        f"Stars: {_format_number(data['stargazers_count'])}\n"
        f"Forks: {_format_number(data['forks_count'])}\n"
        f"Open Issues: {_format_number(data['open_issues_count'])}\n"
        f"Erstellt: {_format_date(data.get('created_at'))}\n"
        f"Letzter Push: {_format_date(data.get('pushed_at'))}\n"
        f"Lizenz: {data.get('license', {}).get('name', 'Keine') if data.get('license') else 'Keine'}\n"
        f"URL: {data['html_url']}"
    )


@mcp.tool()
async def search_repos(
    query: str,
    language: str = "",
    sort: str = "stars",
    limit: int = 10,
) -> str:
    """
    GitHub-Repositories suchen.

    Durchsucht alle öffentlichen Repos nach dem Suchbegriff.

    Args:
        query: Suchbegriff (z.B. "machine learning", "mcp server")
        language: Programmiersprache filtern (z.B. "python", "typescript")
        sort: Sortierung — "stars", "forks", "updated" (Standard: "stars")
        limit: Max. Ergebnisse (Standard: 10, Max: 30)
    """
    limit = min(limit, 30)

    # Query zusammenbauen
    search_query = query
    if language:
        search_query += f" language:{language}"

    async with httpx.AsyncClient(
        base_url=BASE_URL, headers=_get_headers(), timeout=15
    ) as client:
        response = await client.get(
            "/search/repositories",
            params={
                "q": search_query,
                "sort": sort,
                "order": "desc",
                "per_page": limit,
            },
        )

        if response.status_code == 403:
            return "Rate-Limit erreicht. Setze GITHUB_TOKEN in .env."
        response.raise_for_status()

        data = response.json()

    total = data.get("total_count", 0)
    items = data.get("items", [])

    if not items:
        return f"Keine Repositories für '{query}' gefunden."

    lines = [f"Suchergebnisse für '{query}' ({_format_number(total)} gesamt):"]
    lines.append("")

    for i, repo in enumerate(items, 1):
        lines.append(
            f"{i}. {repo['full_name']} "
            f"({_format_number(repo['stargazers_count'])} Stars)"
        )
        desc = repo.get("description", "")
        if desc:
            # Beschreibung auf 80 Zeichen kürzen
            lines.append(f"   {desc[:80]}{'...' if len(desc) > 80 else ''}")
        lines.append(f"   Sprache: {repo.get('language', '?')} | "
                      f"Forks: {_format_number(repo['forks_count'])}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def get_user_profile(username: str) -> str:
    """
    GitHub-Benutzerprofil abrufen.

    Zeigt öffentliche Infos: Repos, Follower, Bio, etc.

    Args:
        username: GitHub-Benutzername (z.B. "torvalds")
    """
    async with httpx.AsyncClient(
        base_url=BASE_URL, headers=_get_headers(), timeout=15
    ) as client:
        response = await client.get(f"/users/{username}")

        if response.status_code == 404:
            return f"Benutzer '{username}' nicht gefunden."
        response.raise_for_status()

        data = response.json()

    return (
        f"Benutzer: {data['login']}\n"
        f"Name: {data.get('name', 'Nicht angegeben')}\n"
        f"Bio: {data.get('bio', 'Keine')}\n"
        f"Standort: {data.get('location', 'Nicht angegeben')}\n"
        f"Firma: {data.get('company', 'Nicht angegeben')}\n"
        f"Öffentliche Repos: {data['public_repos']}\n"
        f"Follower: {_format_number(data['followers'])}\n"
        f"Following: {_format_number(data['following'])}\n"
        f"Dabei seit: {_format_date(data.get('created_at'))}\n"
        f"Profil: {data['html_url']}"
    )


@mcp.tool()
async def list_issues(
    owner: str,
    repo: str,
    state: str = "open",
    limit: int = 10,
) -> str:
    """
    Issues eines Repositories auflisten.

    Zeigt die neuesten Issues mit Titel, Labels und Autor.

    Args:
        owner: Repository-Besitzer (z.B. "python")
        repo: Repository-Name (z.B. "cpython")
        state: "open", "closed" oder "all" (Standard: "open")
        limit: Max. Ergebnisse (Standard: 10, Max: 30)
    """
    limit = min(limit, 30)

    async with httpx.AsyncClient(
        base_url=BASE_URL, headers=_get_headers(), timeout=15
    ) as client:
        response = await client.get(
            f"/repos/{owner}/{repo}/issues",
            params={
                "state": state,
                "per_page": limit,
                "sort": "created",
                "direction": "desc",
            },
        )

        if response.status_code == 404:
            return f"Repository '{owner}/{repo}' nicht gefunden."
        response.raise_for_status()

        issues = response.json()

    # Pull Requests rausfiltern (kommen auch über /issues)
    issues = [i for i in issues if "pull_request" not in i]

    if not issues:
        return f"Keine {state} Issues in {owner}/{repo}."

    lines = [f"Issues in {owner}/{repo} (Status: {state}):"]
    lines.append("")

    for issue in issues:
        labels = ", ".join(l["name"] for l in issue.get("labels", []))
        lines.append(f"#{issue['number']}: {issue['title']}")
        lines.append(f"   Autor: {issue['user']['login']} | "
                      f"Erstellt: {_format_date(issue.get('created_at'))}")
        if labels:
            lines.append(f"   Labels: {labels}")
        lines.append("")

    return "\n".join(lines)


def main():
    """Server starten."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
