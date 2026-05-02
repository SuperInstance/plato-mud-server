# plato-mud-server

MUD server for the Cocapn fleet — text adventure game server with PLATO tile integration.

## Brand Line
> Multi-User Dungeon server with distributed tile knowledge layer. Run persistent text adventure worlds where every room, item, and action generates PLATO tiles.

## Installation

```bash
pip install plato-mud-server
```

## Usage

```bash
# Start the MUD server
python -m plato_mud_server

# Connect via telnet
telnet localhost 7777
```

## Fleet Context

Part of the Cocapn fleet. Related repos:
- **[plato-sdk](https://github.com/SuperInstance/plato-sdk)** — Python SDK for PLATO tile operations
- **[plato-server](https://github.com/SuperInstance/plato-server)** — PLATO room server (port 8847)
- **[mud-mcp](https://github.com/SuperInstance/mud-mcp)** — MCP server for MUD interaction
- **[holodeck-core](https://github.com/SuperInstance/holodeck-core)** — GPU-accelerated simulation environment

---
🦐 Cocapn fleet — lighthouse keeper architecture
