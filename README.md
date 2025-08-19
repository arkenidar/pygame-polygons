# Polygon Drawer (Pygame)

This small app opens a Pygame window where you can build polygons by clicking vertices.

## Usage

1. Create and activate a Python virtual environment (optional but recommended).

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python polygon_draw.py
```

## Controls

- Left click: add vertex
- Right click or Enter: close polygon (requires 3+ vertices)
- Backspace: remove last vertex
- C: clear all polygons
- S: save polygons to polygons.txt (simple CSV-like format)
- Esc: quit

## Notes

- If you run this on a headless server (no display), Pygame will fail to open a window. Run locally or use an environment with an X server.
