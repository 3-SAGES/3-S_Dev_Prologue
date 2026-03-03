import curses
import time
from typing import List
from config import GAME_WIDTH, GAME_HEIGHT, MAP_HEIGHT, MAP_WIDTH, C_PLAYER, C_UI_TEXT, C_UI_HIGHLIGHT, C_ELITE, C_DEFAULT, C_WEAK, TITLE
from utils import safe_addstr

class VisualEffect:
    def __init__(self, x: int, y: int, char: str, color: int, duration: int):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.duration = duration

class VFXManager:
    def __init__(self):
        self.effects: List[VisualEffect] = []

    def add(self, x: int, y: int, char: str, color: int, duration: int = 2):
        self.effects.append(VisualEffect(x, y, char, color, duration))

    def update(self):
        alive = []
        for fx in self.effects:
            fx.duration -= 1
            if fx.duration > 0: alive.append(fx)
        self.effects = alive

class UISystem:
    @staticmethod
    def draw_hud(window, player, level, message_log, last_dmg):
        map_x_start = (GAME_WIDTH - MAP_WIDTH) // 2
        y = MAP_HEIGHT + 1 
        window.move(y, map_x_start) # Move to start of HUD line
        window.clrtoeol() # Clear the line
        
        disp_hp = max(0, player.hp)
        hp_str = f"HP: {disp_hp}/{player.max_hp}"
        safe_addstr(window, y, map_x_start + 2, hp_str, curses.color_pair(C_PLAYER) | curses.A_BOLD)
        
        lvl_str = f"FLOOR {level}"
        center_x = GAME_WIDTH // 2 - (len(lvl_str) // 2)
        safe_addstr(window, y, center_x, lvl_str, curses.color_pair(C_UI_HIGHLIGHT))

        final_log = message_log
        log_x = map_x_start + MAP_WIDTH - len(final_log) - 2
        safe_addstr(window, y, log_x, final_log, curses.color_pair(C_DEFAULT))

    @staticmethod
    def type_text(stdscr, y, x, text, color, delay=0.02):
        for i in range(len(text) + 1):
            safe_addstr(stdscr, y, x, text[:i], color)
            stdscr.refresh()
            time.sleep(delay)

    @staticmethod
    def show_intro(stdscr):

        curses.flushinp() 
        stdscr.nodelay(False)
        stdscr.erase()
        
        time.sleep(1) # Initial pause
        h, w = stdscr.getmaxyx()  # Actual screen dimensions (h, w)
        offset = 16

        title = TITLE
        
        cy = h // 2 - 8
        cx = (w - len(title)) // 2 + offset # Offset cheap fix
        safe_addstr(stdscr, cy, cx, title, curses.color_pair(C_UI_HIGHLIGHT) | curses.A_REVERSE | curses.A_BOLD)
        
        lines = [
            "In the age of silence...",
            "The world was reduced to simple shapes.",
            "One Geometric Soul woke up...",
            "Ascend the 10 floors.",
            "Destroy the Architect!"
        ]
        
        text_y = cy + 4
        for i, line in enumerate(lines):
            cx = (w - len(line)) // 2 + offset # Same offset cheap fix
            UISystem.type_text(stdscr, text_y + (i * 2), cx, line, curses.color_pair(C_UI_TEXT), 0.04)
            time.sleep(0.3)

        curses.flushinp() # Clear input buffer again - DO NOT TOUCH!

        prompt = "[ PRESS ANY KEY TO BEGIN ]"
        py = text_y + (len(lines) * 2) + 3
        px = (w - len(prompt)) // 2 + offset # Same offset cheap fix
        
        while True:
            safe_addstr(stdscr, py, px, prompt, curses.color_pair(C_UI_HIGHLIGHT) | curses.A_BLINK)
            key = stdscr.getch()
            if key != -1: # Any key pressed
                break
        
        stdscr.nodelay(True)

    @staticmethod
    def show_outro(stdscr, victory: bool):
        curses.flushinp()
        stdscr.nodelay(False)
        stdscr.erase()
        
        h, w = stdscr.getmaxyx()
        offset = 16
        
        title = " V I C T O R Y " if victory else " F R A C T U R E D "
        color = C_PLAYER if victory else C_WEAK
        
        cy = h // 2 - 4
        cx = (w - len(title)) // 2 + offset
        safe_addstr(stdscr, cy, cx, title, curses.color_pair(color) | curses.A_REVERSE | curses.A_BOLD)
        
        sub = TITLE
        safe_addstr(stdscr, cy - 2, (w - len(sub)) // 2 + offset, sub, curses.color_pair(C_DEFAULT))

        credits = ["Code & Design: 3'SAGES + GOD_GIVEN_RESOURCES", "Thank you for playing."]
        for i, line in enumerate(credits):
            safe_addstr(stdscr, cy + 3 + i, (w - len(line)) // 2 + offset, line, curses.color_pair(C_DEFAULT))
        
        prompt = "Press 'R' to Restart or 'Q' to Quit"
        safe_addstr(stdscr, cy + 8, (w - len(prompt)) // 2 + offset, prompt, curses.color_pair(C_DEFAULT) | curses.A_BLINK)
        
        while True:
            key = stdscr.getch()
            if key in [ord('q'), ord('Q')]: return 'q'
            if key in [ord('r'), ord('R')]: return 'r'

    @staticmethod
    def show_monolith_menu(window):
        h, w = GAME_HEIGHT, GAME_WIDTH
        mw, mh = 40, 14
        mx, my = (w - mw) // 2, (h - mh) // 2
        
        win = curses.newwin(mh, mw, my, mx)
        win.box()
        win.attron(curses.color_pair(C_UI_HIGHLIGHT))
        win.box()
        win.attroff(curses.color_pair(C_UI_HIGHLIGHT))
        
        win.addstr(1, 2, " T H E   M O N O L I T H ", curses.color_pair(C_UI_HIGHLIGHT) | curses.A_BOLD)
        win.addstr(3, 2, "1. REPAIR GEOMETRY", curses.color_pair(C_DEFAULT))
        win.addstr(4, 5, "(Heal 50% + Max HP)", curses.color_pair(C_ELITE))
        win.addstr(6, 2, "2. SHARPEN EDGES", curses.color_pair(C_DEFAULT))
        win.addstr(7, 5, "(Damage +3)", curses.color_pair(C_ELITE))
        win.addstr(9, 2, "3. SPECIAL UPGRADE", curses.color_pair(C_DEFAULT))
        win.addstr(10, 5, "(Placebo ++)", curses.color_pair(C_ELITE))
        
        win.refresh()
        curses.flushinp()
        while True:
            key = window.getch()
            if key in [ord('1'), ord('2'), ord('3')]:
                del win
                window.touchwin()
                window.refresh()
                return chr(key)
            if key == curses.KEY_RESIZE: return '1'