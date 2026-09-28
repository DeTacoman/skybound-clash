# Skybound Clash

Skybound Clash is a fast-paced 2D platform fighting game built with Python and Pygame.

Choose one of five fighters, battle against a CPU-controlled opponent, use basic attacks and character-specific specials, build your super meter, and knock your opponent out of the arena. Each fighter has three stocks, and the match also has a three-minute time limit.

## Requirements

- Python 3.8 or newer
- Pygame

## Installation

1. Place `main.py`, `requirements.txt`, and this `README.md` in the same folder.
2. Open a terminal in that folder.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the game

Run the following command:

```bash
python main.py
```

## Controls

### Player 1

- `A` / `D` — Move left and right
- `W` or `I` — Jump
- `J` — Basic attack
- `K` — Special attack
- `L` — Shield while grounded, or air dodge while airborne
- `O` — Super attack when the super meter is full

### Menu and match controls

- `1`–`5` — Choose Player 1's fighter from the menu
- `Enter` — Start a match or return from the results screen
- `P` — Pause or resume the match
- `R` — Return to the menu
- `Esc` — Quit the game

Player 2 is controlled by the computer.

## Fighters

- **Aegis** — Defensive fighter with strong guard-based attacks
- **Ember** — Fast fire-based fighter
- **Tide** — Water-themed fighter with projectiles and aerial attacks
- **Volt** — Very fast fighter with teleportation and electric attacks
- **Terra** — Heavy fighter with powerful attacks and high weight

## License

This project is provided as a standalone example game.
