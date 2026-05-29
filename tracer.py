import numpy as np
import config
from config import TRACER, EQ_MODE_STANDARD, EQ_MODE_PARAMETRIC, EQ_MODE_TANGENT
from parser import (
    split_standard, parse_parametric, detect_mode, get_safe_namespace, clean_expression
)

def _snap_standard(left_clean: str, right_clean: str,
                   mx: float, my: float, zoom: float) -> tuple[float, float] | None:

    n = 600
    half = zoom * 0.05
    snap_radius = TRACER["snap_radius"]

    x_scan = np.linspace(mx - snap_radius * 2, mx + snap_radius * 2, n)
    ns_h   = get_safe_namespace({"x": x_scan, "y": np.full_like(x_scan, my)})
    try:
        Zl = eval(left_clean,  ns_h)
        Zr = eval(right_clean, ns_h)
        Z_h = np.array(Zl - Zr, dtype=np.float64)
        sign_changes_h = np.where(np.diff(np.sign(Z_h)))[0]
        best_x = None
        best_dist = snap_radius
        for idx in sign_changes_h:
            z0, z1 = Z_h[idx], Z_h[idx + 1]
            if z1 == z0:
                continue
            frac = -z0 / (z1 - z0)
            x_cross = x_scan[idx] + frac * (x_scan[idx + 1] - x_scan[idx])
            dist = abs(x_cross - mx)
            if dist < best_dist:
                best_dist = dist
                best_x = x_cross
        if best_x is not None:
            return (best_x, my)
    except Exception:
        pass

    y_scan = np.linspace(my - snap_radius * 2, my + snap_radius * 2, n)
    ns_v   = get_safe_namespace({"x": np.full_like(y_scan, mx), "y": y_scan})
    try:
        Zl = eval(left_clean,  ns_v)
        Zr = eval(right_clean, ns_v)
        Z_v = np.array(Zl - Zr, dtype=np.float64)
        sign_changes_v = np.where(np.diff(np.sign(Z_v)))[0]
        best_y = None
        best_dist = snap_radius
        for idx in sign_changes_v:
            z0, z1 = Z_v[idx], Z_v[idx + 1]
            if z1 == z0:
                continue
            frac = -z0 / (z1 - z0)
            y_cross = y_scan[idx] + frac * (y_scan[idx + 1] - y_scan[idx])
            dist = abs(y_cross - my)
            if dist < best_dist:
                best_dist = dist
                best_y = y_cross
        if best_y is not None:
            return (mx, best_y)
    except Exception:
        pass

    return None

def _snap_parametric(x_expr: str, y_expr: str,
                     mx: float, my: float) -> tuple[float, float] | None:
    n = config.RENDER["parametric_points"]
    t = np.linspace(*config.RENDER["t_range"], n)
    ns = get_safe_namespace({"t": t, "x": t, "y": t})
    try:
        Xc = np.array(eval(x_expr, ns), dtype=np.float64)
        Yc = np.array(eval(y_expr, ns), dtype=np.float64)
        dists = (Xc - mx) ** 2 + (Yc - my) ** 2
        idx = int(np.argmin(dists))
        if np.sqrt(dists[idx]) < TRACER["snap_radius"] * 1.5:
            return (float(Xc[idx]), float(Yc[idx]))
    except Exception:
        pass
    return None

def get_snap_point(raw: str, mx: float, my: float,
                   zoom: float) -> tuple[float, float] | None:
    raw = raw.strip()
    if not raw:
        return None

    mode = detect_mode(raw)

    if mode == EQ_MODE_PARAMETRIC:
        parsed = parse_parametric(raw)
        if parsed:
            return _snap_parametric(parsed[0], parsed[1], mx, my)
        return None
    elif mode == EQ_MODE_TANGENT:
        return None
    else:
        try:
            l, r = split_standard(raw)
            return _snap_standard(l, r, mx, my, zoom)
        except Exception:
            return None

class TracerOverlay:

    def __init__(self):
        self._dot   = None
        self._label = None
        self._vline = None
        self._hline = None

    def update(self, ax, snap_pt: tuple[float, float] | None,
               color: str, theme: dict):
        self._clear_artists()

        if snap_pt is None:
            return

        x, y = snap_pt
        dot_color = theme["text_primary"]

        self._dot = ax.scatter(
            [x], [y],
            s=TRACER["dot_size"],
            color=dot_color,
            zorder=8,
            edgecolors=color,
            linewidths=1.8,
        )
        ox, oy = TRACER["label_offset"]
        self._label = ax.annotate(
            f"({x:.3f}, {y:.3f})",
            xy=(x, y),
            xytext=(ox, oy),
            textcoords="offset points",
            fontsize=8,
            color=theme["text_primary"],
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=theme["card_bg"],
                edgecolor=color,
                alpha=0.9,
                linewidth=1.0,
            ),
            zorder=9,
        )
        self._vline = ax.axvline(x, color=color, linewidth=0.6,
                                  linestyle=":", alpha=0.5, zorder=2)
        self._hline = ax.axhline(y, color=color, linewidth=0.6,
                                  linestyle=":", alpha=0.5, zorder=2)

    def _clear_artists(self):
        for attr in ("_dot", "_label", "_vline", "_hline"):
            artist = getattr(self, attr, None)
            if artist is not None:
                try:
                    artist.remove()
                except Exception:
                    pass
                setattr(self, attr, None)

    def clear(self, ax):
        self._clear_artists()