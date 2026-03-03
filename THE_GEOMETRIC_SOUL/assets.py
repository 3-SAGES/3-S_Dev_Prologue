from config import C_WEAK, C_ELITE, C_BOSS, C_STRONG

# ENTITIES
PLAYER_SPRITE = ["Ω"]

ENEMIES = {
    # Tier 1
    "bat": {"char": ["v"], "color_id": C_WEAK, "hp": 32, "dmg": 5, "name": "Vampiric Geometry"},
    "wisp": {"char": ["*"], "color_id": C_WEAK, "hp": 21, "dmg": 4, "name": "Static Wisp"},
    "bug": {"char": ["x"], "color_id": C_WEAK, "hp": 27, "dmg": 6, "name": "Glitch Bug"},

    # Tier 2
    "drone": {"char": ["<o>"], "color_id": C_STRONG, "hp": 58, "dmg": 10, "name": "Hunter Drone"},
    "ghost": {"char": ["(oo)"], "color_id": C_STRONG, "hp": 67, "dmg": 12, "name": "Phantom"},
    "sentinel": {"char": ["[o]", " | "], "color_id": C_STRONG, "hp": 81, "dmg": 12, "name": "Sentinel"},
    
    # Tier 3
    "tank": {"char": ["{##}"], "color_id": C_ELITE, "hp": 105, "dmg": 15, "name": "Heavy Block"},
    "blocker": {"char": ["|==|"], "color_id": C_ELITE, "hp": 84, "dmg": 8, "name": "Wall Unit"},
    "construct": {"char": ["/MM\\", "|xx|"], "color_id": C_ELITE, "hp": 126, "dmg": 14, "name": "Construct"},

    # Boss
    "boss_construct": {
        "char": [
            " \+/ ",
            "< O >",
            " /+\ "
        ],
        "color_id": C_BOSS, "hp": 450, "dmg": 30, "name": "THE ARCHITECT"
    }
}

# MAP CHUNKS (15x10)
CHUNK_OPEN = [
    "...............",
    "...............",
    "...............",
    "...............",
    "...............",
    "...............",
    "...............",
    "...............",
    "...............",
    "..............."
]

CHUNK_PILLARS = [
    "...............",
    ".#...#...#...#.",
    "...............",
    "...............",
    "...............",
    "...............",
    "...............",
    ".#...#...#...#.",
    "...............",
    "..............."
]

CHUNK_CENTER = [
    "...............",
    "...............",
    "...............",
    ".....#####.....",
    ".....#####.....",
    ".....#####.....",
    "...............",
    "...............",
    "...............",
    "..............."
]

CHUNK_MAZE = [
    "...............",
    "...............",
    "...#.......#...",
    ".#.#########.#.",
    ".#...........#.",
    ".#.#########.#.",
    "...#.......#...",
    "...............",
    "...............",
    "..............."
]

MAP_PATTERNS = [CHUNK_OPEN, CHUNK_PILLARS, CHUNK_CENTER, CHUNK_MAZE]

# TILES & ITEMS
TILE_WALL = "▒"
TILE_FLOOR = " "
TILE_DECOR = ["·", "°", "`"]

ITEM_HEART = "♥"
ITEM_WEAPON = "†"

# NARRATIVE
STORY_MESSAGES = {
    1: "The air is stale...",
    3: "You hear gears grinding above...",
    5: "YOU FOUND THE ANCIENT HILT! [F] TO FIRE",
    7: "The architecture is becoming hostile...",
    9: "THERE IS NO TURNING BACK."
}