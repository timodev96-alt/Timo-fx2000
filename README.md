# Timo F(x) 2000

A graphing calculator I built with Python because I was tired of opening a browser just to plot a curve. It works like Desmos but runs fully offline as a desktop app.

![screenshot](https://github.com/user-attachments/assets/099ff2d0-fba1-4617-9700-22e2a608d4d9)

---

## What it can do

It handles more than just `y = f(x)`. You can type in implicit relations, parametric curves, or tangent lines and it figures out what to draw:

- `x^2 + y^2 = 25` — circles and implicit curves work natively
- `x = cos(t), y = sin(t)` — parametric mode, just separate with a comma
- `y = x^2 @ x = 2` — draws the tangent line at that exact point
- Hover over any curve and it snaps to it and shows the coordinates
- When two curves cross, it marks the intersection and prints the point
- Scroll to zoom, middle-mouse drag to pan
- Dark and light theme, toggle in the title bar

---

## Running it

You need Python 3.10+ and two packages:

```bash
pip install numpy matplotlib
python main.py
```

Or just download the Windows executable directly from the releases tab (no Python needed).

[![Download](https://img.shields.io/badge/Download-.exe-blue)](https://github.com/timodev96-alt/Timo-fx2000/releases/download/Timo_f(x)2000/Timof.x.2000.exe)

---

## Building the exe yourself

```bash
pip install pyinstaller
python build.py
```

Puts the output in `dist/TimoFx2000/`. Zip that folder and it runs on any Windows machine.

---

## Equation examples to try

| What | Type this |
|------|-----------|
| Sine wave | `y = sin(x)` |
| Circle | `x^2 + y^2 = 25` |
| Parabola sideways | `x = y^2` |
| Unit circle parametric | `x=cos(t), y=sin(t)` |
| Tangent at a point | `y=x^2 @ x=2` |
| Heart | `((x/6.5)^2 + (y/6.5)^2 - 1)^3 - (x/6.5)^2 * (y/6.5)^3 = 0` |
| Lemniscate | `(x^2 + y^2)^2 = 2*(x^2 - y^2)` |

---

## Project layout

```
├── main.py            entry point
├── config.py          themes, colors, constants
├── parser.py          turns what you type into something numpy can eval
├── renderer.py        draws the curves using matplotlib contour
├── intersection.py    finds where curves cross numerically
├── tracer.py          mouse snapping and coordinate readout
├── build.py           wraps pyinstaller into one command
└── ui/
    ├── layout.py      window, title bar, theme switching
    ├── keypad.py      the button grid on the left
    ├── sidebar.py     equation list on the right
    └── graph_panel.py the matplotlib canvas in the middle
```

---

## Dependencies

```
numpy >= 1.24
matplotlib >= 3.7
tkinter        # ships with Python, no install needed
```

---

## Built with help from AI

I used Claude as a coding assistant throughout this project, bouncing ideas, debugging the contour renderer, and getting the intersection detection to actually work. The architecture decisions, the feature choices, and the overall direction were mine. Claude wrote a lot of the code, I broke it, we fixed it together.

---
