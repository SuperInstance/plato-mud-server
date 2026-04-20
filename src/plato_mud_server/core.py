"""MUD server — text adventure game server."""
import time
from dataclasses import dataclass, field

@dataclass
class Mud_serverConfig:
    name: str = "plato-mud-server"
    enabled: bool = True

class Mud_server:
    def __init__(self, config: Mud_serverConfig = None):
        self.config = config or Mud_serverConfig()
        self._created_at = time.time()
        self._operations: list[dict] = []

    def execute(self, operation: str, **kwargs) -> dict:
        result = {"operation": operation, "status": "ok", "timestamp": time.time()}
        self._operations.append(result)
        return result

    def history(self, limit: int = 50) -> list[dict]:
        return self._operations[-limit:]

    @property
    def stats(self) -> dict:
        return {"operations": len(self._operations), "created": self._created_at,
                "enabled": self.config.enabled}
