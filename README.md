# The Backrooms — Level 0

A 3D first-person liminal horror game. Wander the endless yellow rooms, collect
8 bottles of Almond Water, and no-clip back out of reality — without letting
the thing that lives here find you.

The whole game is seen through the camcorder you're holding — CRT scanlines,
tape grain, barrel distortion, a blinking REC light and running timecode.
Movement has real momentum and head sway, and in some sectors the fluorescent
lights are dead or dying. Occasionally, all of them go out at once.

Built with Python and the Ursina 3D engine (Panda3D). Runs on macOS and Windows.

## How to run

You need Python 3.10+ installed.

**macOS** (Terminal):
```
python3 -m pip install ursina
python3 backrooms.py
```
If `python3` is not found, install it from https://www.python.org/downloads/
or with Homebrew: `brew install python`.

**Windows** (Command Prompt or PowerShell):
```
py -m pip install ursina
py backrooms.py
```
If `py` is not found, install Python from https://www.python.org/downloads/
and check "Add Python to PATH" during installation.

The first launch generates the textures and ambient sound automatically
(a folder called `assets_generated` will appear next to the script).

## Controls

| Key            | Action                  |
|----------------|-------------------------|
| W A S D / Arrows | Move                  |
| Mouse          | Look around             |
| Left Shift     | Sprint (drains stamina) |
| R              | Restart after game over |
| Esc            | Quit                    |

## Rules

- 8 bottles of Almond Water are scattered through the maze. Walk into them
  to collect. Collect all 8 to win.
- A dark entity roams the halls. If it gets line of sight on you, it chases —
  and it is faster than your walking speed. Sprint, break its line of sight
  around corners, and it will lose you.
- The screen tints red as it closes in. If it touches you, it's over.
- The maze, bottle locations, and the entity's position are randomized
  every run.
- Two or three sectors of the maze have dead lights. The camera's gain
  compensates with heavy grain — you can still see, barely. Flickering
  tubes mark the edges of these zones.
- Sometimes every light in the level cuts out for a second or two. When
  they come back, the entity may not be where it was.

## Notes

- Each run generates a new random layout, so no two descents are the same.
- If the game runs slowly, close other apps — it is lightweight, but the
  first launch can take a few seconds while Python warms up.
