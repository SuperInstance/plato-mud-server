"""Text adventure MUD server with rooms, exits, NPCs, and player state."""
import time
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

@dataclass
class Room:
    name: str
    description: str = ""
    exits: dict[str, str] = field(default_factory=dict)  # direction -> room_id
    items: list[str] = field(default_factory=list)
    npcs: list[str] = field(default_factory=list)

@dataclass
class Npc:
    name: str
    room_id: str
    dialogue: list[str] = field(default_factory=list)
    inventory: list[str] = field(default_factory=list)
    greeting: str = ""

@dataclass
class Player:
    name: str
    room_id: str = "start"
    inventory: list[str] = field(default_factory=list)
    score: int = 0
    commands_issued: int = 0
    connected: bool = True
    connected_at: float = field(default_factory=time.time)

class MudServer:
    def __init__(self, name: str = "PLATO MUD"):
        self.name = name
        self._rooms: dict[str, Room] = {}
        self._players: dict[str, Player] = {}
        self._npcs: dict[str, Npc] = {}
        self._global_inventory: dict[str, list[str]] = defaultdict(list)
        self._command_log: list[dict] = []
        self._tick = 0

    def add_room(self, room_id: str, name: str, description: str = "",
                 exits: dict[str, str] = None) -> Room:
        room = Room(name=name, description=description, exits=exits or {})
        self._rooms[room_id] = room
        return room

    def connect_rooms(self, room_a: str, direction_a: str, room_b: str, direction_b: str = ""):
        if room_a in self._rooms:
            self._rooms[room_a].exits[direction_a] = room_b
        if room_b in self._rooms and direction_b:
            self._rooms[room_b].exits[direction_b] = room_a

    def add_npc(self, npc_id: str, name: str, room_id: str, dialogue: list[str] = None,
                greeting: str = "") -> Npc:
        npc = Npc(name=name, room_id=room_id, dialogue=dialogue or [], greeting=greeting)
        self._npcs[npc_id] = npc
        if room_id in self._rooms:
            self._rooms[room_id].npcs.append(npc_id)
        return npc

    def add_item(self, item: str, room_id: str = ""):
        if room_id and room_id in self._rooms:
            self._rooms[room_id].items.append(item)
        else:
            self._global_inventory["world"].append(item)

    def player_join(self, name: str, start_room: str = "start") -> Player:
        player = Player(name=name, room_id=start_room)
        self._players[name] = player
        return player

    def player_leave(self, name: str) -> Optional[Player]:
        player = self._players.get(name)
        if player:
            player.connected = False
        return player

    def process_command(self, player_name: str, command: str) -> str:
        player = self._players.get(player_name)
        if not player or not player.connected:
            return "You are not connected."
        player.commands_issued += 1
        self._tick += 1
        cmd = command.strip().lower()
        self._command_log.append({"player": player_name, "command": cmd,
                                   "room": player.room_id, "tick": self._tick})
        if len(self._command_log) > 2000:
            self._command_log = self._command_log[-2000:]

        if cmd in ("look", "l", "ls"):
            return self._look(player)
        elif cmd.startswith("go ") or cmd in ("n", "s", "e", "w", "u", "d"):
            direction = cmd.split()[-1] if cmd.startswith("go ") else cmd
            direction_map = {"n": "north", "s": "south", "e": "east", "w": "west", "u": "up", "d": "down"}
            direction = direction_map.get(direction, direction)
            return self._move(player, direction)
        elif cmd.startswith("take ") or cmd.startswith("get "):
            return self._take(player, cmd.split(maxsplit=1)[-1])
        elif cmd.startswith("drop "):
            return self._drop(player, cmd.split(maxsplit=1)[-1])
        elif cmd.startswith("talk ") or cmd.startswith("say "):
            return self._talk(player, cmd.split(maxsplit=1)[-1])
        elif cmd == "inventory" or cmd == "i":
            return self._inventory(player)
        elif cmd == "score":
            return f"Score: {player.score}"
        elif cmd == "help":
            return "Commands: look, go <dir>, n/s/e/w, take <item>, drop <item>, talk <npc>, inventory, score, help"
        elif cmd == "exits":
            room = self._rooms.get(player.room_id)
            if room and room.exits:
                return "Exits: " + ", ".join(room.exits.keys())
            return "No visible exits."
        else:
            return f"Unknown command: {command}"

    def _look(self, player: Player) -> str:
        room = self._rooms.get(player.room_id)
        if not room:
            return "You see nothing."
        lines = [room.name]
        if room.description:
            lines.append(room.description)
        if room.exits:
            lines.append("Exits: " + ", ".join(room.exits.keys()))
        if room.items:
            lines.append("Items: " + ", ".join(room.items))
        npc_names = [self._npcs[n].name for n in room.npcs if n in self._npcs]
        if npc_names:
            lines.append("NPCs: " + ", ".join(npc_names))
        return "\n".join(lines)

    def _move(self, player: Player, direction: str) -> str:
        room = self._rooms.get(player.room_id)
        if not room or direction not in room.exits:
            return f"You can't go {direction}."
        player.room_id = room.exits[direction]
        return self._look(player)

    def _take(self, player: Player, item: str) -> str:
        room = self._rooms.get(player.room_id)
        if not room:
            return "Nothing to take."
        item_lower = item.lower()
        for i, room_item in enumerate(room.items):
            if item_lower in room_item.lower():
                room.items.pop(i)
                player.inventory.append(room_item)
                player.score += 1
                return f"Taken: {room_item}"
        return f"No '{item}' here."

    def _drop(self, player: Player, item: str) -> str:
        item_lower = item.lower()
        for i, inv_item in enumerate(player.inventory):
            if item_lower in inv_item.lower():
                player.inventory.pop(i)
                room = self._rooms.get(player.room_id)
                if room:
                    room.items.append(inv_item)
                return f"Dropped: {inv_item}"
        return f"No '{item}' in inventory."

    def _talk(self, player: Player, target: str) -> str:
        room = self._rooms.get(player.room_id)
        if not room:
            return "Nobody to talk to."
        target_lower = target.lower()
        for npc_id in room.npcs:
            npc = self._npcs.get(npc_id)
            if npc and target_lower in npc.name.lower():
                if npc.greeting:
                    return f"{npc.name}: {npc.greeting}"
                if npc.dialogue:
                    return f"{npc.name}: {npc.dialogue[0]}"
                return f"{npc.name} has nothing to say."
        return f"No '{target}' here."

    def _inventory(self, player: Player) -> str:
        if not player.inventory:
            return "You are carrying nothing."
        return "Inventory: " + ", ".join(player.inventory)

    def get_room_description(self, room_id: str) -> str:
        room = self._rooms.get(room_id)
        if not room:
            return "Unknown room"
        return f"{room.name}: {room.description or '(no description)'} — exits: {list(room.exits.keys())}"

    @property
    def stats(self) -> dict:
        online = sum(1 for p in self._players.values() if p.connected)
        return {"rooms": len(self._rooms), "players": len(self._players),
                "online": online, "npcs": len(self._npcs),
                "commands_processed": self._tick, "world_items": len(self._global_inventory.get("world", []))}
