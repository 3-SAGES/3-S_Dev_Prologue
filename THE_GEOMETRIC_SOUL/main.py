import curses
import os
import traceback
from utils import force_terminal_settings
from engine import GameEngine
from config import TITLE, GAME_WIDTH, GAME_HEIGHT

def main(stdscr):
    
    curses.curs_set(0)
    stdscr.nodelay(True)
    
    stdscr.timeout(30)
    
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
    
    game = GameEngine(stdscr)
    game.run()

if __name__ == "__main__":
    if os.name == 'nt':
        os.system(f"title {TITLE}")
        force_terminal_settings(GAME_WIDTH, GAME_HEIGHT)
    
    try:
        # Why ARROW_UP = ESC [ A ?!
        os.environ.setdefault('ESCDELAY', '25')
        curses.wrapper(main)
    except Exception as e:
        if os.name == 'nt':
            os.system("mode con: cols=120 lines=40")
        print("THE GEOMETRY FRACTURED (CRASH REPORT):")
        print(e)
        traceback.print_exc()
        input("\nPress ENTER to close...")