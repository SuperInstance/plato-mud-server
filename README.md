# plato-mud-server

[![PyPI](https://img.shields.io/pypi/v/plato-mud-server)](https://pypi.org/project/plato-mud-server/) [![Python](https://img.shields.io/pypi/pyversions/plato-mud-server)](https://pypi.org/project/plato-mud-server/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MUD server — text adventure game server. pip install plato-mud-server

## Installation

```bash
pip install plato-mud-server
```

## Usage

Text-based agent training ground with 16 rooms, navigation, and skill development.

```python
from plato_mud_server import MUDClient

client = MUDClient("oracle1")
client.look()       # See current room
client.go("north")  # Navigate
client.examine("terminal")  # Interact
```

## License

MIT — see [LICENSE](LICENSE)