# MCP Server Starter Kit

## Build Your Own MCP Server in 5 Minutes

This kit gives you everything you need to build, test, and publish a production-ready MCP (Model Context Protocol) server that AI agents can use.

## What's Inside

```
mcp-starter-kit/
├── template/           # Ready-to-use project template
│   ├── pyproject.toml  # Pre-configured build system
│   ├── src/
│   │   ├── server.py          # FastMCP server (fill in your tools)
│   │   ├── config.py          # Settings & environment variables
│   │   ├── tools/example.py   # Example tool with detailed comments
│   │   └── clients/example_client.py  # Example API client
│   ├── .gitignore
│   └── .mcp.json       # Claude Code integration config
├── examples/
│   ├── joke_server/    # Beginner: Random jokes API
│   ├── github_server/  # Intermediate: GitHub API wrapper
│   └── multi_api_server/ # Advanced: Multiple APIs combined
├── GUIDE.md            # Step-by-step tutorial
└── CHECKLIST.md        # Pre-launch checklist
```

## Quick Start

### 1. Copy the template

```bash
cp -r template/ my-mcp-server/
cd my-mcp-server/
```

### 2. Rename placeholders

Open `pyproject.toml` and replace:
- `your-mcp-server` with your server name
- `your_mcp_server` with your Python package name
- `Your Name` with your name
- `your-github-username` with your GitHub username

### 3. Add your first tool

Edit `src/tools/example.py` — follow the comments to add your own tools.

### 4. Test locally

```bash
pip install -e .
your-mcp-server  # Runs via stdio
```

### 5. Publish to PyPI

```bash
pip install build twine
python -m build
python -m twine upload dist/*
```

That's it. Your MCP server is live and installable via `pip install your-mcp-server`.

## Learning Path

| Level | Example | What You'll Learn |
|-------|---------|-------------------|
| Beginner | `joke_server/` | Basic tool, simple API call |
| Intermediate | `github_server/` | Auth, error handling, multiple tools |
| Advanced | `multi_api_server/` | Multiple APIs, caching, complex tools |

## Requirements

- Python 3.10+
- `pip install mcp` (MCP SDK)

## Support

- Issues: [GitHub Issues](https://github.com/AiAgentKarl/mcp-starter-kit/issues)
- MCP Docs: [modelcontextprotocol.io](https://modelcontextprotocol.io)

## License

MIT License — use this for anything, commercial or personal.
