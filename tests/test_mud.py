"""Tests for MUD server core functionality."""
import pytest
from plato_mud_server.mud import MudServer, Room, Player


class TestRoom:
    def test_room_creation_with_defaults(self):
        room = Room(name="Test Room")
        assert room.name == "Test Room"
        assert room.description == ""
        assert room.exits == {}
        assert room.items == []
        assert room.npcs == []

    def test_room_creation_with_exits(self):
        room = Room(name="Crossroads", description="A four-way intersection", exits={"north": "north_room"})
        assert room.name == "Crossroads"
        assert room.exits == {"north": "north_room"}

    def test_room_items_initially_empty(self):
        room = Room(name="Empty Chamber")
        assert room.items == []


class TestPlayer:
    def test_player_creation_defaults(self):
        player = Player(name="TestPlayer")
        assert player.name == "TestPlayer"
        assert player.room_id == "start"
        assert player.inventory == []
        assert player.score == 0
        assert player.commands_issued == 0
        assert player.connected is True

    def test_player_creation_custom_start(self):
        player = Player(name="Adventurer", room_id="entrance")
        assert player.room_id == "entrance"


class TestMudServer:
    def test_server_naming(self):
        server = MudServer(name="TestServer")
        assert server.name == "TestServer"

    def test_server_default_name(self):
        server = MudServer()
        assert server.name == "PLATO MUD"

    def test_add_room(self):
        server = MudServer()
        room = server.add_room("room1", "First Room", "A small room")
        assert room is not None
        assert room.name == "First Room"
        assert "room1" in server._rooms

    def test_add_multiple_rooms(self):
        server = MudServer()
        server.add_room("r1", "Room One")
        server.add_room("r2", "Room Two")
        assert len(server._rooms) == 2

    def test_connect_rooms(self):
        server = MudServer()
        server.add_room("north", "North Room")
        server.add_room("south", "South Room")
        server.connect_rooms("north", "south", "south", "north")
        assert server._rooms["north"].exits.get("south") == "south"
        assert server._rooms["south"].exits.get("north") == "north"

    def test_connect_rooms_one_way(self):
        server = MudServer()
        server.add_room("start", "Start Room")
        server.add_room("end", "End Room")
        server.connect_rooms("start", "east", "end")
        assert server._rooms["start"].exits.get("east") == "end"
        assert "west" not in server._rooms["end"].exits

    def test_add_npc(self):
        server = MudServer()
        server.add_room("room1", " tavern")
        npc = server.add_npc("npc1", "Innkeeper", "room1", greeting="Welcome!")
        assert npc is not None
        assert npc.name == "Innkeeper"
        assert "npc1" in server._npcs

    def test_npc_added_to_room(self):
        server = MudServer()
        server.add_room("room1", "Tavern")
        server.add_npc("npc1", "Barkeep", "room1")
        assert "npc1" in server._rooms["room1"].npcs

    def test_add_item_to_room(self):
        server = MudServer()
        server.add_room("room1", "Chamber")
        server.add_item("Gold Key", "room1")
        assert "Gold Key" in server._rooms["room1"].items

    def test_add_item_global(self):
        server = MudServer()
        server.add_item("Magic Wand")
        assert "Magic Wand" in server._global_inventory["world"]

    def test_player_join(self):
        server = MudServer()
        server.add_room("start", "Start")
        player = server.player_join("Alice")
        assert player is not None
        assert player.name == "Alice"
        assert "Alice" in server._players

    def test_player_join_custom_start(self):
        server = MudServer()
        server.add_room("lobby", "Lobby")
        player = server.player_join("Bob", "lobby")
        assert player.room_id == "lobby"

    def test_player_leave(self):
        server = MudServer()
        server.add_room("start", "Start")
        server.player_join("Charlie")
        player = server.player_leave("Charlie")
        assert player is not None
        assert player.connected is False

    def test_player_leave_not_found(self):
        server = MudServer()
        player = server.player_leave("Ghost")
        assert player is None

    def test_disconnected_player_command(self):
        server = MudServer()
        server.add_room("start", "Start")
        server.player_join("Dave")
        server.player_leave("Dave")
        result = server.process_command("Dave", "look")
        assert result == "You are not connected."


class TestCommands:
    def setup_method(self):
        self.server = MudServer()
        self.server.add_room("start", "Start Room", "The beginning", exits={"north": "hallway", "east": "garden"})
        self.server.add_room("hallway", "Hallway", "A long corridor")
        self.server.add_room("garden", "Garden", "A beautiful garden")
        self.server.player_join("Tester", "start")

    def test_look_command(self):
        result = self.server.process_command("Tester", "look")
        assert "Start Room" in result
        assert "The beginning" in result

    def test_look_shortcut(self):
        result = self.server.process_command("Tester", "l")
        assert "Start Room" in result

    def test_go_direction(self):
        result = self.server.process_command("Tester", "go north")
        assert "Hallway" in result

    def test_north_shortcut(self):
        result = self.server.process_command("Tester", "n")
        assert "Hallway" in result

    def test_south_shortcut(self):
        # Start room has exits north and east, no south exit
        result = self.server.process_command("Tester", "s")
        assert "can't go" in result.lower()

    def test_invalid_direction(self):
        result = self.server.process_command("Tester", "go up")
        assert "can't go up" in result.lower() or "You can't" in result

    def test_take_item(self):
        self.server.add_item("Sword", "start")
        result = self.server.process_command("Tester", "take Sword")
        assert "Taken" in result

    def test_take_get_alias(self):
        self.server.add_item("Potion", "start")
        result = self.server.process_command("Tester", "get Potion")
        assert "Taken" in result

    def test_take_item_not_present(self):
        result = self.server.process_command("Tester", "take Nothing")
        assert "No 'nothing' here" in result

    def test_drop_item(self):
        self.server.add_item("Shield", "start")
        self.server.process_command("Tester", "take Shield")
        result = self.server.process_command("Tester", "drop Shield")
        assert "Dropped" in result

    def test_drop_item_not_in_inventory(self):
        result = self.server.process_command("Tester", "drop Missing")
        assert "No 'missing' in inventory" in result

    def test_inventory_command(self):
        self.server.add_item("Helm", "start")
        self.server.process_command("Tester", "take Helm")
        result = self.server.process_command("Tester", "inventory")
        assert "Helm" in result

    def test_inventory_shortcut(self):
        result = self.server.process_command("Tester", "i")
        assert "nothing" in result.lower() or "Inventory" in result

    def test_score_command(self):
        result = self.server.process_command("Tester", "score")
        assert "Score" in result

    def test_help_command(self):
        result = self.server.process_command("Tester", "help")
        assert "look" in result.lower() or "Commands" in result

    def test_exits_command(self):
        result = self.server.process_command("Tester", "exits")
        assert "north" in result.lower() or "east" in result.lower()

    def test_unknown_command(self):
        result = self.server.process_command("Tester", "dance")
        assert "Unknown command" in result


class TestNPCs:
    def setup_method(self):
        self.server = MudServer()
        self.server.add_room("room1", "Tavern")
        self.server.add_npc("barkeep", "Barkeep", "room1", greeting="Good day!")
        self.server.player_join("Traveler", "room1")

    def test_talk_to_npc_with_greeting(self):
        result = self.server.process_command("Traveler", "talk Barkeep")
        assert "Barkeep" in result
        assert "Good day" in result

    def test_talk_say_alias(self):
        result = self.server.process_command("Traveler", "say Barkeep")
        assert "Barkeep" in result

    def test_talk_partial_name_match(self):
        result = self.server.process_command("Traveler", "talk bark")
        assert "Barkeep" in result

    def test_talk_npc_not_present(self):
        result = self.server.process_command("Traveler", "talk Ghost")
        assert "No 'ghost' here" in result


class TestLookOutput:
    def setup_method(self):
        self.server = MudServer()
        self.server.add_room("start", "Main Hall", "A grand hall", exits={"north": "north"})
        self.server.add_item("Candle", "start")
        self.server.add_npc("servant", "Servant", "start", greeting="At your service")
        self.server.player_join("Visitor", "start")

    def test_look_shows_exits(self):
        result = self.server.process_command("Visitor", "look")
        assert "Exits" in result
        assert "north" in result

    def test_look_shows_items(self):
        result = self.server.process_command("Visitor", "look")
        assert "Items" in result
        assert "Candle" in result

    def test_look_shows_npcs(self):
        result = self.server.process_command("Visitor", "look")
        assert "NPCs" in result
        assert "Servant" in result


class TestScoring:
    def setup_method(self):
        self.server = MudServer()
        self.server.add_room("start", "Start")
        self.server.add_item("Gem", "start")
        self.server.player_join("Scorer", "start")

    def test_take_increments_score(self):
        self.server.process_command("Scorer", "take Gem")
        player = self.server._players["Scorer"]
        assert player.score == 1

    def test_multiple_takes_increment_score(self):
        self.server.add_item("Coin", "start")
        self.server.process_command("Scorer", "take Gem")
        self.server.process_command("Scorer", "take Coin")
        player = self.server._players["Scorer"]
        assert player.score == 2


class TestCommandLog:
    def setup_method(self):
        self.server = MudServer()
        self.server.add_room("start", "Start")
        self.server.player_join("Logger", "start")

    def test_commands_logged(self):
        self.server.process_command("Logger", "look")
        assert len(self.server._command_log) == 1

    def test_command_log_capped(self):
        for i in range(2100):
            self.server.process_command("Logger", "look")
        assert len(self.server._command_log) == 2000


class TestStats:
    def setup_method(self):
        self.server = MudServer()
        self.server.add_room("room1", "Room 1")
        self.server.add_npc("npc1", "NPC", "room1")
        self.server.player_join("P1")
        self.server.player_join("P2")

    def test_stats_rooms(self):
        assert self.server.stats["rooms"] == 1

    def test_stats_players(self):
        assert self.server.stats["players"] == 2

    def test_stats_npcs(self):
        assert self.server.stats["npcs"] == 1


class TestGetRoomDescription:
    def setup_method(self):
        self.server = MudServer()
        self.server.add_room("room1", "Big Chamber", "A spacious room", exits={"north": "room2"})
        self.server.add_room("room2", "Small Chamber", "")

    def test_existing_room(self):
        desc = self.server.get_room_description("room1")
        assert "Big Chamber" in desc
        assert "spacious" in desc
        assert "north" in desc

    def test_unknown_room(self):
        desc = self.server.get_room_description("nonexistent")
        assert desc == "Unknown room"

    def test_room_without_description(self):
        desc = self.server.get_room_description("room2")
        assert "Small Chamber" in desc
        assert "no description" in desc