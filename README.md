# 📈 Timo F(x) 2000

A powerful Desmos-style graphing calculator built with Python, Tkinter, NumPy and Matplotlib.

---

## ✨ Features

- **Implicit equation graphing** — plot any relation like `x^2 + y^2 = 25`, not just `y = f(x)`
- **Parametric curves** — enter `x=cos(t), y=sin(t)` for full parametric support
- **Derivative / tangent overlay** — use `y=x^2 @ x=2` to draw the tangent line at any point
- **Intersection detection** — automatically finds and labels where curves cross
- **Curve tracer** — hover your mouse near any curve to snap and read precise coordinates
- **Adaptive resolution** — fast low-res preview while typing, sharp high-res on settle
- **Dual theme** — clean dark and light modes with one click
- **Zoom & pan** — scroll wheel to zoom, middle-mouse drag to pan
- **Per-equation controls** — toggle visibility, cycle color, switch mode per row

---

## 🖥 Screenshots

> Dark mode — Heart curve on launch

> <img width="1401" height="695" alt="image" src="https://github.com/user-attachments/assets/099ff2d0-fba1-4617-9700-22e2a608d4d9" />


```
((x/6.5)^2 + (y/6.5)^2 - 1)^3 - (x/6.5)^2 * (y/6.5)^3 = 0
```

---

## 🚀 Quick Start

### Option A — Run from source

```bash
# 1. Clone the repo
git clone https://github.com/timodev96-alt/Timo-fx2000.git
cd timo-fx-2000

# 2. Install dependencies
pip install numpy matplotlib

# 3. Run
python main.py
```
# or ![Download Timo f(x) 2000](https://github.com/timodev96-alt/Timo-fx2000/releases/download/Timo_f(x)2000/Timof.x.2000.exe)
### Option B — Build a standalone executable

```bash
pip install numpy matplotlib pyinstaller
python build.py
```

Output: `dist/TimoFx2000/TimoFx2000.exe` (Windows) or `dist/TimoFx2000/TimoFx2000` (Mac/Linux)

---

## 📁 Project Structure

```
Graphical Calculator/
├── main.py              # Entry point
├── config.py            # Themes, constants, color palette
├── parser.py            # Syntax engine (implicit multiply, trig, parametric)
├── renderer.py          # Adaptive contour + parametric + tangent renderer
├── intersection.py      # Numerical intersection detection
├── tracer.py            # Mouse curve-snapping tracer
├── build.py             # PyInstaller build script
├── requirements.txt     # pip dependencies
└── ui/
    ├── layout.py        # Root window, theme controller, event wiring
    ├── keypad.py        # Calculator button panel
    ├── sidebar.py       # Equation manager sidebar
    └── graph_panel.py   # Matplotlib canvas, zoom, pan, control bar
```


---

## 🧮 Equation Examples

| Type | Example |
|------|---------|
| Explicit | `y = sin(x)` |
| Implicit | `x^2 + y^2 = 25` |
| Vertical line | `x = 3` |
| Parametric | `x=cos(t), y=sin(t)` |
| Tangent line | `y=x^2 @ x=2` |
| Heart curve | `((x/6.5)^2 + (y/6.5)^2 - 1)^3 - (x/6.5)^2 * (y/6.5)^3 = 0` |
| Lemniscate | `(x^2 + y^2)^2 = 2*(x^2 - y^2)` |

---

## 📦 Dependencies

```
numpy >= 1.24
matplotlib >= 3.7
tkinter (included with Python)
```
🤖 AI Disclosure

This project utilized [Claude code] for:

    - Writing boilerplate code and optimizing algorithms.
    - Debugging error messages.

---

## 📄 License

MIT License — free to use, modify and distribute.
