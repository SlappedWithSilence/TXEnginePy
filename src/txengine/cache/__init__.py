# Variables
from ..systems.item.item import Item

# Config caches

config: dict[str, any] = {
    "debug": False,
    "primary_stat": "health",
    "primary_skill": "combat",
    "primary_current": "cash-cash-money"
}

game_files: dict[str, str] = {
    "item": "items.json",
    "room": "rooms.json",
    "conversation": "conversations.json",
    "stat": "entity.json",
    "combat_entity": "combat_entities.json",
    "recipe": "recipes.json",
    "skill": "skills.json",
    "faction": "factions.json"
}

# Game-Resource caches
#   Do NOT access these unless strictly necessary.

# int-indexed
item_map: dict[int, Item] = {}
conversation_map: dict[int, any] = {}  # TODO: Add typing
combat_entity_map: dict[int, any] = {}  # TODO: Add typing

# str-indexed
stats_map: dict[str, tuple[int, int]] = {}
ability_map: dict[str, any] = {}  # TODO: Add typing





