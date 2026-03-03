# THE GEOMETRIC SOUL

**The Geometric Soul** is a terminal-based arcade *roguelike* game written in Python. The project uses the `curses` library for real-time ASCII graphics rendering, featuring procedurally generated levels and dynamic combat.

## 🌌 Lore:

In the era of silence, the **Architect** appeared. A being of infinite precision deemed the chaos of reality a flaw and "fixed" it, reducing all of spacetime into basic geometric shapes. The complexity of life was flattened into static solids.

You awaken as the **Geometric Soul** – an anomaly that has retained memories of the old world. Your goal is to climb through the 10 floors of the Architect's tower and destroy its guardians.

Your only weapons are **Waves** – mathematical oscillations (sine waves) that possess the ability to bend the perfect edges created by the Architect. You must introduce dissonance into this perfect harmony to restore the world to its original, chaotic shape.

## 📋 Requirements and Installation

### System Requirements
*   **Python 3.12+** (recommended).
*   OS: Windows, Linux, or macOS.

### Dependencies Installation
The game uses the `curses` library.
*   **Linux / macOS:** The library is usually built-in.
*   **Windows:** Requires installing a wrapper. Open the terminal in the project folder and type:

```bash
pip install windows-curses
```

## ⚙️ Running and Configuration (VS Code)

The game is launched via the `main.py` file:

```bash
python main.py
```

### ⚠️ Important Note for VS Code Users
The integrated terminal in Visual Studio Code often misinterprets the `curses` library (issues with color rendering and refreshing) as well as keyboard shortcuts.

**The game was tested and should be run in an EXTERNAL TERMINAL (CMD / PowerShell / Terminal).**

To configure this in VS Code:
1. Open the `.vscode/launch.json` file (or create a new launch configuration).
2. Add or change the `"console"` option to `"externalTerminal"`.

Example configuration:
```json
{
    "version": "0.2.0",
    "configurations":[
        {
            "name": "Python: External Terminal",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "externalTerminal"
        }
    ]
}
```

## 🎮 Controls

| Key | Action |
| :---: | :--- |
| **Arrows** | Movement (Up, Down, Left, Right) |
| **SPACEBAR** | Melee attack (Phase Cut) |
| **F** | Ranged attack (requires finding a weapon) |
| **Q** | Quit game |
| **R** | Restart (after death or victory) |

### Developer Mode (Cheats)
*   **G** – God Mode (Invincibility).
*   **K** – Smite (Kills all enemies on the map).

## 🏗️ Project Structure

The game code is divided into modules following the object-oriented paradigm to separate game logic from rendering and data.

*   **`main.py`**: Entry point. Initializes the `curses` library, sets up colors, and passes control to the game engine.
*   **`engine.py`**: The heart of the game (`GameEngine`). Handles the Game Loop, input logic, world state updates, and rendering calls.
*   **`entities.py`**: Game object definitions.
    *   `Player`: Player stats, combat system.
    *   `Enemy` / `Boss`: Enemy AI, simple tracking algorithms.
*   **`map_system.py`**: Procedural map generation. Uses a "stamp" (chunk) system to create random room layouts while maintaining playability.
*   **`ui_system.py`**: Responsible for the visual layer of the interface (HUD, logs, intro, "Monolith" upgrade menu).
*   **`assets.py`**: Visual database (enemy ASCII art, map block definitions).
*   **`config.py`**: Configuration constants (map dimensions, gameplay balance, color palette).
*   **`utils.py`**: System utilities, including Windows API hacks to force the correct console window size and font.