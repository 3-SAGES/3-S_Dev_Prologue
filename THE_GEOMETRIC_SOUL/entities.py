import random
from typing import List, Tuple
from config import C_ITEM, C_PLAYER, MAP_WIDTH, MAP_HEIGHT
from assets import PLAYER_SPRITE, ENEMIES

class Entity:
    def __init__(self, x: int, y: int, sprite: List[str], color_id: int, name: str):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.base_color = color_id
        self.color = color_id
        self.name = name
        self.hp = 10
        self.max_hp = 10
        self.hit_flash = 0
        self.height = len(sprite)
        self.width = max(len(row) for row in sprite) if self.height > 0 else 0

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def get_occupied_tiles(self, offset_x=0, offset_y=0) -> List[Tuple[int, int]]:
        tiles = []
        for r, row in enumerate(self.sprite):
            for c, char in enumerate(row):
                if char != " ":
                    tiles.append((self.x + offset_x + c, self.y + offset_y + r))
        return tiles

    def take_damage(self, amount: int):
        self.hp -= amount
        self.hit_flash = 2 # Snappy flash

    def can_move(self, dx: int, dy: int, game_map, entities):
        future_tiles = self.get_occupied_tiles(dx, dy)
        for tx, ty in future_tiles:
            if not (0 <= tx < MAP_WIDTH and 0 <= ty < MAP_HEIGHT): return False
            if not game_map.tiles[ty][tx].walkable: return False
            for ent in entities:
                if ent is not self and ent.hp > 0:
                    if (ent.x <= tx < ent.x + ent.width and ent.y <= ty < ent.y + ent.height):
                            if (tx, ty) in ent.get_occupied_tiles(): return False
        return True

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

class Player(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, PLAYER_SPRITE, C_PLAYER, "Hero")
        self.hp = 150
        self.max_hp = 150
        self.damage = 14
        self.xp = 0
        self.level = 1
        self.invincible = False # God Mode flag
        self.has_weapon = False
        self.facing_dir = (1, 0)
        self.invincibility_timer = 0

    def heal(self, amount: int):
        self.hp = min(self.hp + amount, self.max_hp)
    
    def take_damage(self, amount: int):
        if not self.invincible and self.invincibility_timer == 0:
            self.hp -= amount
            self.hit_flash = 2
            self.invincibility_timer = 5

class Enemy(Entity):
    def __init__(self, x: int, y: int, type_key: str):
        data = ENEMIES.get(type_key, ENEMIES["bat"])
        super().__init__(x, y, data["char"], data["color_id"], data["name"])
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.damage = data["dmg"] 
        self.type_key = type_key
        self.move_timer = 0
        self.stun_timer = 0
        self.touch_cooldown = 0 
        self.move_threshold = 10 
        if "bat" in type_key: self.move_threshold = 5

    def update(self, player, game_map, entities) -> Tuple[int, int]:
        if self.stun_timer > 0: self.stun_timer -= 1
        if self.touch_cooldown > 0: self.touch_cooldown -= 1
        if self.hit_flash > 0: self.hit_flash -= 1
        if self.stun_timer > 0: return (0, 0)

        self.move_timer += 1
        if self.move_timer < self.move_threshold: return (0, 0)
        self.move_timer = 0
        
        target_x, target_y = player.center
        my_cx, my_cy = self.center
        dx = 1 if target_x > my_cx else -1
        dy = 1 if target_y > my_cy else -1
        
        move_x, move_y = 0, 0
        if random.random() > 0.5: move_x = dx
        else: move_y = dy
        
        if self.can_move(move_x, move_y, game_map, entities):
            self.move(move_x, move_y)
            return (move_x, move_y)
        return (0, 0)

class Boss(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "boss_construct")
        self.move_threshold = 12
        self.attack_timer = 0
        self.color_timer = 0
        self.burst_remaining = 0
        self.burst_delay = 0
        
    def update(self, player, game_map, entities):
        self.color_timer += 1
        if self.color_timer > 2:
            self.color_timer = 0
            self.color = random.choice([2, 3, 4, 5, 8, 9]) 

        self.attack_timer += 1
        if self.burst_delay > 0: self.burst_delay -= 1
        
        return super().update(player, game_map, entities)

class Item:
    def __init__(self, x: int, y: int, kind: str):
        self.x = x
        self.y = y
        self.kind = kind
        self.char = "♥" if kind == "heart" else "†"
        self.color = C_ITEM 

class Projectile:
    def __init__(self, x: int, y: int, dx: int, dy: int, is_enemy: bool = False):
        self.x = float(x)
        self.y = float(y)
        self.dx = float(dx)
        self.dy = float(dy)
        self.is_enemy = is_enemy
        self.char = "*" if not is_enemy else "o"
        self.damage = 10 if not is_enemy else 20
    
    def update(self):
        speed = 1.0 if self.is_enemy else 1.5
        self.x += self.dx * speed
        self.y += self.dy * speed
    
    @property
    def pos(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)