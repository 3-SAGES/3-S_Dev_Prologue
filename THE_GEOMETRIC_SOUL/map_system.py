import random
from typing import Tuple
from assets import TILE_WALL, TILE_FLOOR, TILE_DECOR, MAP_PATTERNS

class Tile:
    def __init__(self, char: str, walkable: bool):
        self.char = char
        self.walkable = walkable
        self.is_exit = False
        self.is_locked = False

class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = []
        self.exit_pos = None
        self.chunk_w = 15
        self.chunk_h = 10

    def generate_level(self, level):
        self.tiles = [[Tile(TILE_WALL, False) for _ in range(self.width)] for _ in range(self.height)]
        
        cols = self.width // self.chunk_w
        rows = self.height // self.chunk_h
        
        for r in range(rows):
            for c in range(cols):
                pattern = random.choice(MAP_PATTERNS)
                off_x = c * self.chunk_w
                off_y = r * self.chunk_h
                self._stamp(pattern, off_x, off_y)
                
        for y in range(self.height):
            for x in range(self.width):
                if x==0 or x==self.width-1 or y==0 or y==self.height-1:
                    self.tiles[y][x].char = TILE_WALL
                    self.tiles[y][x].walkable = False

        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if self.tiles[y][x].walkable and random.random() < 0.02: 
                    self.tiles[y][x].char = random.choice(TILE_DECOR)

        self._place_exit()

    def _stamp(self, pattern, off_x, off_y):
        for y, row in enumerate(pattern):
            for x, char in enumerate(row):
                if off_x+x >= self.width or off_y+y >= self.height: continue
                if char == ".":
                    self.tiles[off_y+y][off_x+x].char = TILE_FLOOR
                    self.tiles[off_y+y][off_x+x].walkable = True

    def _place_exit(self):
        for _ in range(100):
            x = random.randint(self.width//2, self.width-2)
            y = random.randint(self.height//2, self.height-2)
            if self.tiles[y][x].walkable:
                self.tiles[y][x].is_exit = True
                self.tiles[y][x].is_locked = True
                self.tiles[y][x].char = "+"
                self.exit_pos = (x, y)
                return

    def get_valid_spawn(self, entities_to_avoid=None) -> Tuple[int, int]:
        for _ in range(2000):
            x = random.randint(2, self.width-3)
            y = random.randint(2, self.height-3)
            if not self.tiles[y][x].walkable: continue
            
            overlap = False
            if entities_to_avoid:
                for ent in entities_to_avoid:
                    if abs(ent.x - x) < 2 and abs(ent.y - y) < 2:
                        overlap = True
                        break
            if overlap: continue
            return x, y
        return 5, 5