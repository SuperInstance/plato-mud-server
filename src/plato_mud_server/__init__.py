"""MUD server — text adventure game server with room navigation and NPCs.
Part of the PLATO framework."""
from .mud import MudServer, Room, Player, Npc
__version__ = "0.1.0"
__all__ = ["MudServer", "Room", "Player", "Npc"]
