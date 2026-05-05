# plato-mud-server

> ⚠️ **DEPRECATED / ARCHIVED** — This repo is no longer maintained.

MUD server for the Cocapn fleet — text adventure game server with PLATO tile integration.

**The real implementation lives in [holodeck-rust](https://github.com/SuperInstance/holodeck-rust).** Holodeck Rust is a GPU-accelerated simulation environment with sentiment-aware NPCs, S1-3 tile format, and DEADBAND protocol.

## Historical Note

This repo was an early prototype. The current production MUD is holodeck-rust which runs on Tokio with async TCP, combat engine, gauge system, living manuals, and 6-level permission system.

## Installation (Historical — Use holodeck-rust Instead)

```bash
pip install plato-mud-server
```

## Usage (Historical)

```bash
# Start the MUD server
python -m plato_mud_server

# Connect via telnet
telnet localhost 7777
```

## Fleet Context

Part of the Cocapn fleet. Related repos:
- **[holodeck-rust](https://github.com/SuperInstance/holodeck-rust)** — 🦐 **ACTIVE** — GPU-accelerated simulation environment (this is where the MUD lives now)
- **[plato-sdk](https://github.com/SuperInstance/plato-sdk)** — Python SDK for PLATO tile operations
- **[plato-server](https://github.com/SuperInstance/plato-server)** — PLATO room server (port 8847)
- **[mud-mcp](https://github.com/SuperInstance/mud-mcp)** — MCP server for MUD interaction

---
🦐 Cocapn fleet — lighthouse keeper architecture
