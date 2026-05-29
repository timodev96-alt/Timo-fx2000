import numpy as np
import config
from parser import (
    get_safe_namespace, split_standard, parse_parametric, parse_tangent,
    detect_mode, clean_expression
)
from config import EQ_MODE_STANDARD, EQ_MODE_PARAMETRIC, EQ_MODE_TANGENT, RENDER

def _numerical_derivative(expr: str, x_val: float, h: float = 1e-5) -> float | None:
    try:
        ns_p = get_safe_namespace({"x": x_val + h, "y": 0.0, "t": 0.0})
        ns_m = get_safe_namespace({"x": x_val - h, "y": 0.0, "t": 0.0})
        fp = float(eval(expr, ns_p))
        fm = float(eval(expr, ns_m))
        if not (np.isfinite(fp) and np.isfinite(fm)):
            return None
        return (fp - fm) / (2 * h)
    except Exception:
        return None


def _eval_at(expr: str, x_val: float) -> float | None:
    try:
        ns = get_safe_namespace({"x": x_val, "y": 0.0, "t": 0.0})
        result = float(eval(expr, ns))
        return result if np.isfinite(result) else None
    except Exception:
        return None

def render_tangent(ax, raw: str, color: str, zoom: float, theme: dict) -> bool:
    parsed = parse_tangent(raw)
    if parsed is None:
        return False

    base_expr, x0 = parsed

    y0 = _eval_at(base_expr, x0)
    if y0 is None:
        return False

    slope = _numerical_derivative(base_expr, x0)
    if slope is None:
        return False

    x_range = np.linspace(-zoom * 1.5, zoom * 1.5, 400)
    y_line  = y0 + slope * (x_range - x0)

    ax.plot(
        x_range, y_line,
        color=color,
        linewidth=RENDER["tangent_linewidth"],
        linestyle="--",
        alpha=0.85,
        zorder=3,
    )
    ax.scatter(
        [x0], [y0],
        color=color,
        s=40,
        zorder=5,
        edgecolors=theme["text_primary"],
        linewidths=0.8,
    )
    return True

def render_parametric(ax, raw: str, color: str, theme: dict) -> bool:
    parsed = parse_parametric(raw)
    if parsed is None:
        return False

    x_expr, y_expr = parsed
    t_min, t_max = RENDER["t_range"]
    t = np.linspace(t_min, t_max, RENDER["parametric_points"])
    ns = get_safe_namespace({"t": t, "x": t, "y": t})

    try:
        X = eval(x_expr, ns)
        Y = eval(y_expr, ns)

        dX = np.abs(np.diff(X))
        dY = np.abs(np.diff(Y))
        threshold = 10
        mask = np.concatenate(([True], (dX < threshold) & (dY < threshold)))

        X_masked = np.where(mask, X, np.nan)
        Y_masked = np.where(mask, Y, np.nan)

        ax.plot(
            X_masked, Y_masked,
            color=color,
            linewidth=RENDER["linewidth"],
            zorder=3,
        )
        return True
    except Exception:
        return False


def render_standard(ax, raw: str, color: str, zoom: float, resolution: int) -> bool:
    if not raw or raw.strip() in ("", "0", "Error", "Invalid"):
        return False

    try:
        left_clean, right_clean = split_standard(raw)
    except Exception:
        return False

    x_arr = np.linspace(-zoom * 1.5, zoom * 1.5, resolution)
    y_arr = np.linspace(-zoom * 1.5, zoom * 1.5, resolution)
    X, Y  = np.meshgrid(x_arr, y_arr)

    ns = get_safe_namespace({"x": X, "y": Y})

    try:
        Z_left  = eval(left_clean,  ns)
        Z_right = eval(right_clean, ns)
        Z = np.array(Z_left - Z_right, dtype=np.float64)

        if np.all(Z > 0) or np.all(Z < 0):
            return True   # valid expression, just no crossing in current view

        ax.contour(
            X, Y, Z,
            levels=[0],
            colors=[color],
            linewidths=RENDER["linewidth"],
            zorder=3,
        )
        return True
    except Exception:
        return False

def render_equation(ax, raw: str, color: str, zoom: float,
                    resolution: int, theme: dict) -> bool:
    raw = raw.strip()
    if not raw:
        return False

    mode = detect_mode(raw)

    if mode == EQ_MODE_PARAMETRIC:
        return render_parametric(ax, raw, color, theme)
    elif mode == EQ_MODE_TANGENT:
        return render_tangent(ax, raw, color, zoom, theme)
    else:
        return render_standard(ax, raw, color, zoom, resolution)

def style_axis(ax, fig, zoom: float, theme: dict, show_grid: bool = True):
    ax.clear()

    bg  = theme["graph_bg"]
    ax.set_facecolor(bg)
    fig.set_facecolor(theme["graph_fg"])

    spine_color = theme["axis_color"]
    for spine in ax.spines.values():
        spine.set_color(spine_color)
        spine.set_linewidth(0.8)

    ax.tick_params(colors=theme["text_secondary"], labelsize=8)

    if show_grid:
        ax.grid(
            True,
            color=theme["grid_color"],
            linewidth=0.6,
            linestyle="-",
            alpha=0.9,
        )
    else:
        ax.grid(False)

    ax.axhline(0, color=theme["axis_zero_color"], linewidth=1.0, zorder=2)
    ax.axvline(0, color=theme["axis_zero_color"], linewidth=1.0, zorder=2)

    ax.set_xlim([-zoom, zoom])
    ax.set_ylim([-zoom, zoom])