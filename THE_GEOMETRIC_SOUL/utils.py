import os
import time
import curses

# WINDOWS API SECTION
if os.name == 'nt':
    import ctypes
    from ctypes import wintypes

    class CONSOLE_FONT_INFOEX(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("nFont", ctypes.c_ulong),
            ("dwFontSize", wintypes._COORD),
            ("FontFamily", ctypes.c_uint),
            ("FontWeight", ctypes.c_uint),
            ("FaceName", ctypes.c_wchar * 32)
        ]

def _calculate_optimal_font_size(width, height) -> int:
    if os.name != 'nt': return 16
    try:
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        MARGIN_Y = 80
        max_h = (screen_height - MARGIN_Y) // (height + 2)
        return max(10, min(max_h, 32))
    except: return 16

def force_terminal_settings(width=120, height=40):
    if os.name != 'nt': return
    font_h = _calculate_optimal_font_size(width, height)
    font = CONSOLE_FONT_INFOEX()
    font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
    font.nFont = 0
    font.dwFontSize.X = 0
    font.dwFontSize.Y = font_h
    font.FontFamily = 54
    font.FontWeight = 400
    font.FaceName = "Consolas"

    try:
        handle = ctypes.windll.kernel32.GetStdHandle(-11) # Active Console Output Buffer
        ctypes.windll.kernel32.SetCurrentConsoleFontEx(handle, False, ctypes.byref(font))
    except: pass

    os.system(f"mode con: cols={width+2} lines={height+2}")
    
    # Simulate F11
    time.sleep(0.1)
    ctypes.windll.user32.keybd_event(0x7A, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0x7A, 0, 0x0002, 0)

# SAFE ADDSTR FUNCTION - USE! /basic one hates non-mechanical beings/
def safe_addstr(win: curses.window, y: int, x: int, text: str, attr: int = 0): 
    try:
        max_y, max_x = win.getmaxyx()
        if y >= max_y or x >= max_x: return
        available = max_x - x - 1
        if len(text) > available: text = text[:available]
        if available > 0: win.addstr(y, x, text, attr)
    except curses.error: pass