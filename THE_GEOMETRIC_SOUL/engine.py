import curses
import curses.textpad
import time
import random
from typing import Optional, List

from config import (
    GAME_WIDTH, GAME_HEIGHT, MAX_LEVELS, MAP_WIDTH, MAP_HEIGHT,
    START_WITH_WEAPON, GOD_MODE_ENABLED,
    C_DEFAULT, C_PLAYER, C_WEAK, C_STRONG, C_ELITE, C_BOSS, 
    C_WALL, C_UI_TEXT, C_UI_HIGHLIGHT, C_DOOR, C_ITEM
)
from assets import STORY_MESSAGES
from utils import safe_addstr
from map_system import GameMap
from entities import Player, Enemy, Boss, Projectile, Item
from ui_system import UISystem, VFXManager

class GameEngine:
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.game_window: Optional[curses.window] = None
        self.is_running = True
        
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(C_DEFAULT, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(C_PLAYER, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(C_WEAK, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(C_STRONG, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(C_ELITE, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(C_BOSS, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(C_WALL, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(C_UI_TEXT, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(C_UI_HIGHLIGHT, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(C_DOOR, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(C_ITEM, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        self.game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
        self.vfx = VFXManager()
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        
        if START_WITH_WEAPON: self.player.has_weapon = True
        if GOD_MODE_ENABLED: self.player.invincible = True

        self.level = 1
        self.enemies: List[Enemy] = []
        self.items: List[Item] = []
        self.projectiles: List[Projectile] = []
        self.game_over = False
        self.victory = False
        self.exit_unlocked = False
        self.last_dmg_dealt = 0

        UISystem.show_intro(self.stdscr)
        self.start_new_level()

    def reset_game(self):
        self.level = 1
        self.game_over = False
        self.victory = False
        
        # Reset Player Stats
        self.player.max_hp = 150
        self.player.hp = 150
        self.player.damage = 15
        self.player.xp = 0
        self.player.has_weapon = START_WITH_WEAPON
        self.player.x, self.player.y = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.player.invincibility_timer = 0
        
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.vfx.effects = []
        
        self.start_new_level()
        self.message_log = "CYCLE RESTARTED."

    def start_new_level(self):
        self.game_map.generate_level(self.level)
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.exit_unlocked = False
        
        px, py = self.game_map.get_valid_spawn(entities_to_avoid=[])
        self.player.x, self.player.y = px, py
        
        self._spawn_wave()
        
        for _ in range(random.randint(1, 3)):
            ix, iy = self.game_map.get_valid_spawn(entities_to_avoid=self.enemies)
            self.items.append(Item(ix, iy, "heart"))

        if self.level == 5 and not self.player.has_weapon:
            wx, wy = self.game_map.get_valid_spawn(entities_to_avoid=self.enemies)
            self.items.append(Item(wx, wy, "weapon"))
            self.message_log = "A LEGENDARY WEAPON APPEARED!"
        else:
            msg = STORY_MESSAGES.get(self.level, "")
            self.message_log = msg if msg else f"Floor {self.level}."

    def _spawn_wave(self):
        if self.level == MAX_LEVELS:
            bx, by = self.game_map.width//2, self.game_map.height//2
            self.enemies = [Boss(bx, by)]
            self.message_log = "THE ARCHITECT HAS AWOKEN."
            return

        budget = 5 + (self.level * 4)
        options = ["bat", "wisp", "bug"]
        if self.level >= 3: options.extend(["drone", "ghost"])
        if self.level >= 5: options.extend(["sentinel", "blocker"])
        if self.level >= 7: options.extend(["tank", "construct"])
        
        while budget > 0:
            key = random.choice(options)
            cost = 3 if key in ["drone", "ghost"] else 1
            if key in ["tank", "sentinel", "blocker"]: cost = 5
            
            ex, ey = self.game_map.get_valid_spawn(entities_to_avoid=self.enemies)
            self.enemies.append(Enemy(ex, ey, key))
            budget -= cost

    def update(self):
        if self.game_over: return

        # Items
        for item in self.items[:]:
            if self.player.x == item.x and self.player.y == item.y:
                if item.kind == "heart":
                    self.player.heal(30)
                    self.message_log = "Picked up Heart (+30 HP)"
                elif item.kind == "weapon":
                    self.player.has_weapon = True
                    self.message_log = "WEAPON ACQUIRED! PRESS 'F' TO FIRE!"
                self.items.remove(item)

        self._update_projectiles()
        self._update_enemies()

        if len(self.enemies) == 0 and not self.exit_unlocked:
            self._unlock_exit()

        self.vfx.update()
        
        # Player Updates
        self.player.hit_flash = max(0, self.player.hit_flash - 1)
        self.player.invincibility_timer = max(0, self.player.invincibility_timer - 1)
        
        if self.player.hp <= 0: 
            self.player.hp = 0
            self.game_over = True

    def _update_projectiles(self):
        for p in self.projectiles[:]:
            p.update()
            px, py = p.pos
            
            if px < 0 or px >= MAP_WIDTH or py < 0 or py >= MAP_HEIGHT:
                if p in self.projectiles: self.projectiles.remove(p)
                continue

            if not self.game_map.tiles[py][px].walkable:
                if p in self.projectiles: self.projectiles.remove(p)
                self.vfx.add(px, py, ".", C_DEFAULT, 1)
                continue
            
            if p.is_enemy:
                if int(self.player.x) == px and int(self.player.y) == py:
                    # Player.take_damage does i-frames check
                    self.player.take_damage(p.damage)
                    self.message_log = f"Took {p.damage} damage from Energy!"
                    if p in self.projectiles: self.projectiles.remove(p)
            else:
                for e in self.enemies:
                    if (px, py) in e.get_occupied_tiles():
                        e.take_damage(p.damage)
                        self.last_dmg_dealt = p.damage
                        self.message_log = f"Hit {e.name} for {p.damage}!"
                        if p in self.projectiles: self.projectiles.remove(p)
                        break

    def _update_enemies(self):
        alive = []
        for enemy in self.enemies:
            enemy.update(self.player, self.game_map, self.enemies)
            
            # Boss Logic
            if isinstance(enemy, Boss):
                if enemy.attack_timer > 40:
                    enemy.attack_timer = 0
                    cx, cy = enemy.center
                    tx, ty = self.player.center
                    
                    if random.random() < 0.6: # Single Shot
                        shot_y = cy + random.choice([-1, 0, 1])
                        diff_x, diff_y = tx - cx, ty - shot_y
                        mag = max(abs(diff_x), abs(diff_y)) or 1
                        self.projectiles.append(Projectile(cx, shot_y, diff_x/mag, diff_y/mag, True))
                    else: # Wave Init
                        enemy.burst_remaining = 3
                        enemy.burst_delay = 0

                # Wave Execute
                if enemy.burst_remaining > 0 and enemy.burst_delay == 0:
                    cx, cy = enemy.center
                    tx, ty = self.player.center
                    diff_x, diff_y = tx - cx, ty - cy
                    mag = max(abs(diff_x), abs(diff_y)) or 1
                    dx, dy = diff_x/mag, diff_y/mag
                    
                    self.projectiles.append(Projectile(cx, cy - 1, dx, dy, True))
                    self.projectiles.append(Projectile(cx, cy,     dx, dy, True))
                    self.projectiles.append(Projectile(cx, cy + 1, dx, dy, True))
                    enemy.burst_remaining -= 1
                    enemy.burst_delay = 8

            # Contact Damage (Enemy moving into Player or overlapping)
            if enemy.touch_cooldown == 0:
                dist_x = abs(enemy.center[0] - self.player.center[0])
                dist_y = abs(enemy.center[1] - self.player.center[1])
                
                # Check ~Overlap or ~Adjacent
                if dist_x <= 1 and dist_y <= 1:
                    if self.player.invincibility_timer == 0 and not self.player.invincible: # Check ?doubled logic? (player.take_damage)
                        self.player.take_damage(enemy.damage) 
                        enemy.touch_cooldown = 15
                        self.message_log = f"Took {enemy.damage} dmg from {enemy.name}!"

            if enemy.hp > 0:
                alive.append(enemy)
            else:
                self.player.xp += 10
        self.enemies = alive

    def _unlock_exit(self):
        if self.game_map.exit_pos:
            ex, ey = self.game_map.exit_pos
            self.game_map.tiles[ey][ex].is_locked = False
            self.game_map.tiles[ey][ex].char = ">"
            self.message_log = "THE WAY IS OPEN."
            self.exit_unlocked = True

    def handle_input(self):
        try:
            key = self.stdscr.getch()
        except: return

        if key == curses.KEY_RESIZE:
            self.stdscr.clear(); self.stdscr.refresh(); self.game_window = None; return
        if key == ord('q'): self.is_running = False
        
        # CHEATS
        if key == ord('g'):
            self.player.invincible = not self.player.invincible
            self.message_log = f"GOD MODE: {self.player.invincible}"
        if key == ord('k') and self.player.invincible:
             for e in self.enemies: e.hp = 0
             self.message_log = "SMITE!"
        
        if self.game_over: return

        dx, dy = 0, 0
        if key == curses.KEY_UP:    dy = -1
        elif key == curses.KEY_DOWN:  dy = 1
        elif key == curses.KEY_LEFT:  dx = -1
        elif key == curses.KEY_RIGHT: dx = 1

        if dx != 0 or dy != 0:
            self.player.facing_dir = (dx, dy)
            dest_x = self.player.x + dx
            dest_y = self.player.y + dy
            
            # COLLISION CHECK: Player walking into Enemy
            enemy_hit = None
            for e in self.enemies:
                if (dest_x, dest_y) in e.get_occupied_tiles():
                    enemy_hit = e
                    break
            
            if enemy_hit:
                # Spike Damage
                self.player.take_damage(enemy_hit.damage)
                self.message_log = f"Ran into {enemy_hit.name}! Took {enemy_hit.damage} dmg!"
            else:
                # Normal Movement
                if 0 <= dest_x < MAP_WIDTH and 0 <= dest_y < MAP_HEIGHT:
                    if self.game_map.tiles[dest_y][dest_x].walkable:
                        self.player.move(dx, dy)
                        tile = self.game_map.tiles[dest_y][dest_x]
                        if tile.is_exit and not tile.is_locked: self._next_level()

        if key == ord(' '): self._perform_melee_attack()
        if key == ord('f') or key == ord('F'):
            if self.player.has_weapon: self._fire_projectile()

    def _perform_melee_attack(self):
        fx, fy = self.player.facing_dir
        
        # Check 2 Tiles Forward
        tx1, ty1 = self.player.x + fx, self.player.y + fy
        tx2, ty2 = self.player.x + (fx*2), self.player.y + (fy*2)
        
        # Visuals
        slash_char = "~"
        if fx == -1: slash_char = "~"
        elif fy == 0: slash_char = "~"
        elif fx == 0: slash_char = "~"
            
        self.vfx.add(tx1, ty1, slash_char, C_PLAYER, duration=3)
        self.vfx.add(tx2, ty2, slash_char, C_PLAYER, duration=3) # Tip
        
        hit = False
        # Collect enemies in range
        hit_enemies = []
        for enemy in self.enemies:
            tiles = enemy.get_occupied_tiles()
            if (tx1, ty1) in tiles or (tx2, ty2) in tiles:
                hit_enemies.append(enemy)

        for enemy in hit_enemies:
            enemy.take_damage(self.player.damage)
            self.last_dmg_dealt = self.player.damage
            hit = True
            self.message_log = f"Hit {enemy.name} for {self.player.damage}!"

        if not hit:
            # Spark if hitting wall
            if not self.game_map.tiles[ty1][tx1].walkable:
                self.vfx.add(tx1, ty1, ".", C_DEFAULT, duration=1)

    def _fire_projectile(self):
        dx, dy = self.player.facing_dir
        px, py = self.player.x + dx, self.player.y + dy
        proj = Projectile(px, py, dx, dy)
        self.projectiles.append(proj)

    def _next_level(self):
        if self.level >= MAX_LEVELS:
            self.victory = True
            self.game_over = True
        else:
            choice = UISystem.show_monolith_menu(self.game_window)
            if choice == '1': 
                self.player.max_hp += 10
                self.player.heal(50)
            elif choice == '2': 
                self.player.damage += 3
            elif choice == '3': pass 
            self.level += 1
            self.start_new_level()

    def render(self):
        try:
            h, w = self.stdscr.getmaxyx()
        except: return
        
        if h < GAME_HEIGHT or w < GAME_WIDTH:
            self.stdscr.erase()
            safe_addstr(self.stdscr, 0, 0, "RESIZE WINDOW - MOUSE + SCROLL TO ZOOM")
            self.stdscr.refresh()
            return

        sy = max(0, (GAME_HEIGHT - MAP_HEIGHT) // 2 - 1)
        sx = max(0, (GAME_WIDTH - MAP_WIDTH) // 2)
        if self.game_window is None:
            self.game_window = curses.newwin(GAME_HEIGHT, GAME_WIDTH, 0, 0)
        win = self.game_window
        win.erase()
        map_off_x, map_off_y = sx + 1, sy + 1
        
        border_color = C_WALL
        if self.game_over:
            border_color = C_PLAYER if self.victory else C_WEAK
        
        win.attron(curses.color_pair(border_color))
        curses.textpad.rectangle(win, sy, sx, sy + MAP_HEIGHT + 1, sx + MAP_WIDTH + 1)
        win.attroff(curses.color_pair(border_color))
        
        frame = (int(time.time() * 5))
        
        # Draw Map
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                tile = self.game_map.tiles[y][x]
                if tile.char != " ":
                    attr = curses.A_NORMAL
                    if tile.char == "▒": attr = curses.color_pair(C_WALL)
                    elif tile.is_exit: 
                        color = C_DOOR if tile.is_locked else (C_DEFAULT if frame % 2 == 0 else C_DOOR)
                        attr = curses.color_pair(color) | curses.A_BOLD
                    try: win.addch(y + map_off_y, x + map_off_x, tile.char, attr)
                    except: pass

        # Draw Items
        for item in self.items:
            color = C_DEFAULT
            if self.player.hp < (self.player.max_hp - 25) and item.kind == "heart":
                color = C_ITEM
            if item.kind != "heart": 
                color = C_UI_TEXT if frame % 2 == 0 else C_ITEM
            try: win.addch(item.y + map_off_y, item.x + map_off_x, item.char, curses.color_pair(color) | curses.A_BOLD)
            except: pass

        # Draw Enemies
        for e in self.enemies:
            attr = curses.color_pair(e.color)
            if e.hit_flash > 0:
                attr = curses.color_pair(C_WEAK) | curses.A_REVERSE | curses.A_BOLD
            for r, row in enumerate(e.sprite):
                for c, char in enumerate(row):
                    if char != " ":
                        try: win.addch(e.y + r + map_off_y, e.x + c + map_off_x, char, attr)
                        except: pass

        # Draw Player
        p_attr = curses.color_pair(C_PLAYER) | curses.A_BOLD
        if self.player.hit_flash > 0:
            p_attr = curses.color_pair(C_WEAK) | curses.A_REVERSE
        try: win.addch(self.player.y + map_off_y, self.player.x + map_off_x, self.player.sprite[0], p_attr)
        except: pass

        # Draw Projectiles & VFX
        for p in self.projectiles:
            color = C_PLAYER if not p.is_enemy else C_BOSS
            try: win.addch(int(p.y) + map_off_y, int(p.x) + map_off_x, p.char, curses.color_pair(color) | curses.A_BOLD)
            except: pass
        for fx in self.vfx.effects:
            try: win.addch(fx.y + map_off_y, fx.x + map_off_x, fx.char, curses.color_pair(fx.color) | curses.A_BOLD)
            except: pass

        UISystem.draw_hud(win, self.player, self.level, self.message_log, self.last_dmg_dealt)

        win.noutrefresh()
        curses.doupdate()

    def run(self):
        while self.is_running:
            self.handle_input()
            self.update()
            self.render()
            
            if self.game_over:
                time.sleep(1)
                choice = UISystem.show_outro(self.stdscr, victory=self.victory)
                if choice == 'q': self.is_running = False
                elif choice == 'r': self.reset_game()