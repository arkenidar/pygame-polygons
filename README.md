# Polygon Drawer (Pygame)

This small app opens a Pygame window where you can build polygons by clicking vertices.

### **Design Philosophy** ( according to ClaudeAI that evaluates it ) ( extracted from longer text )

The entire implementation reflects a **principled approach to computational geometry**:

- **Reliability over cleverness**: Chooses mathematically sound methods over potentially faster but fragile optimizations
- **Clarity over conciseness**: Code is structured for understanding and maintenance
- **Robustness over performance**: Handles edge cases gracefully, even at some computational cost
- **Modularity over monoliths**: Each function is a reusable geometric primitive

This is exactly the kind of implementation you'd want to find in production code—not just because it works, but because it's **maintainable, extensible, and trustworthy**.

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
