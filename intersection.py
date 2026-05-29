# intersection.py — Numerical intersection detection between curve pairs
#
# Strategy:
#   1. Evaluate each equation as Z_i(x,y) = F_i - G_i on a coarse shared grid
#   2. Find cells where Z_1 and Z_2 have *opposite signs simultaneously*
#      (i.e. both cross zero in the same neighbourhood)
#   3. Use scipy.optimize.brentq (or a bisection fallback) to refine each
#      candidate to within INTERSECT["tolerance"]
#   4. Deduplicate points that are closer than a pixel-width threshold

import numpy as np
import config
from config import INTERSECT
from parser import split_standard, get_safe_namespace, detect_mode, parse_parametric
from config import EQ_MODE_STANDARD, EQ_MODE_PARAMETRIC


# ── Grid evaluator ────────────────────────────────────────────────────────────

def _eval_implicit(left_clean: str, right_clean: str,
                   X: np.ndarray, Y: np.ndarray) -> np.ndarray | None:
    """Return Z = left - right evaluated on meshgrid X,Y. None on error."""
    ns = get_safe_namespace({"x": X, "y": Y})
    try:
        Zl = eval(left_clean, ns)
        Zr = eval(right_clean, ns)
        return np.array(Zl - Zr, dtype=np.float64)
    except Exception:
        return None


def _eval_parametric_curve(x_expr: str, y_expr: str,
                            n: int = 2000) -> tuple[np.ndarray, np.ndarray] | None:
    """Sample a parametric curve and return (X_arr, Y_arr)."""
    t = np.linspace(*config.RENDER["t_range"], n)
    ns = get_safe_namespace({"t": t, "x": t, "y": t})
    try:
        X = np.array(eval(x_expr, ns), dtype=np.float64)
        Y = np.array(eval(y_expr, ns), dtype=np.float64)
        return X, Y
    except Exception:
        return None


# ── Point deduplication ───────────────────────────────────────────────────────

def _deduplicate(points: list[tuple[float, float]],
                 tol: float = 0.3) -> list[tuple[float, float]]:
    """
    Remove duplicate intersection points closer than tol graph-units.
    Adjacent grid cells along a curve can each produce a nearby candidate;
    we cluster them and return the centroid of each cluster.
    tol=0.3 is generous — true distinct intersections are always further apart.
    """
    if not points:
        return []

    used = [False] * len(points)
    clusters = []
    for i, p in enumerate(points):
        if used[i]:
            continue
        cluster = [p]
        used[i] = True
        for j, q in enumerate(points):
            if not used[j]:
                if abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol:
                    cluster.append(q)
                    used[j] = True
        clusters.append(cluster)

    unique = []
    for cluster in clusters:
        cx = sum(p[0] for p in cluster) / len(cluster)
        cy = sum(p[1] for p in cluster) / len(cluster)
        unique.append((cx, cy))
    return unique


# ── Sign-change refinement ────────────────────────────────────────────────────

def _refine_intersection(left1, right1, left2, right2,
                         x0, x1, y0, y1) -> tuple[float, float] | None:
    """
    Given a small cell [x0,x1] x [y0,y1] where the two Z surfaces seem to
    cross simultaneously, bisect in both dimensions to find a refined point.
    """
    iters = INTERSECT["refine_iters"]
    tol   = INTERSECT["tolerance"]

    xm = (x0 + x1) / 2
    ym = (y0 + y1) / 2

    def both_near_zero(x, y):
        ns = get_safe_namespace({"x": np.float64(x), "y": np.float64(y)})
        try:
            z1 = float(eval(left1, ns)) - float(eval(right1, ns))
            z2 = float(eval(left2, ns)) - float(eval(right2, ns))
            return abs(z1) + abs(z2)
        except Exception:
            return 1e10

    for _ in range(iters):
        if (x1 - x0) < tol and (y1 - y0) < tol:
            break
        candidates = [
            (x0, y0), (xm, ym), (x1, y1),
            (x0, ym), (x1, ym), (xm, y0), (xm, y1),
        ]
        best = min(candidates, key=lambda p: both_near_zero(*p))
        # Tighten the box around the best candidate
        dx = (x1 - x0) / 2
        dy = (y1 - y0) / 2
        x0, x1 = best[0] - dx / 2, best[0] + dx / 2
        y0, y1 = best[1] - dy / 2, best[1] + dy / 2
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2

    residual = both_near_zero(xm, ym)
    if residual < 0.5:   # loose threshold — good enough for display
        return (xm, ym)
    return None


# ── Main intersection finder ──────────────────────────────────────────────────

def find_intersections(raw1: str, raw2: str,
                       zoom: float) -> list[tuple[float, float]]:
    """
    Find intersection points of two equations within the current zoom window.
    Supports standard/implicit vs standard/implicit only (parametric skipped).
    Returns list of (x, y) tuples.
    """
    mode1 = detect_mode(raw1)
    mode2 = detect_mode(raw2)

    # Only handle standard×standard for now
    if mode1 != EQ_MODE_STANDARD or mode2 != EQ_MODE_STANDARD:
        return []

    try:
        l1, r1 = split_standard(raw1)
        l2, r2 = split_standard(raw2)
    except Exception:
        return []

    res = INTERSECT["grid_res"]
    x_arr = np.linspace(-zoom, zoom, res)
    y_arr = np.linspace(-zoom, zoom, res)
    X, Y  = np.meshgrid(x_arr, y_arr)

    Z1 = _eval_implicit(l1, r1, X, Y)
    Z2 = _eval_implicit(l2, r2, X, Y)

    if Z1 is None or Z2 is None:
        return []

    # Find cells where both Z1 and Z2 change sign (absolute values are small)
    # Strategy: look for cells where product of signs at corners switches
    candidates = []

    dx = x_arr[1] - x_arr[0]
    dy = y_arr[1] - y_arr[0]

    for j in range(res - 1):
        for i in range(res - 1):
            # Cell corners
            z1_vals = [Z1[j, i], Z1[j, i+1], Z1[j+1, i], Z1[j+1, i+1]]
            z2_vals = [Z2[j, i], Z2[j, i+1], Z2[j+1, i], Z2[j+1, i+1]]

            # Both sign-change within the cell?
            z1_min, z1_max = min(z1_vals), max(z1_vals)
            z2_min, z2_max = min(z2_vals), max(z2_vals)

            if (z1_min < 0 < z1_max) and (z2_min < 0 < z2_max):
                x0_cell = x_arr[i]
                y0_cell = y_arr[j]
                candidates.append((x0_cell, x0_cell + dx,
                                   y0_cell, y0_cell + dy))

    points = []
    for (x0, x1, y0, y1) in candidates:
        pt = _refine_intersection(l1, r1, l2, r2, x0, x1, y0, y1)
        if pt is not None:
            points.append(pt)

    return _deduplicate(points)


# ── Matplotlib overlay ────────────────────────────────────────────────────────

def draw_intersections(ax, points: list[tuple[float, float]], theme: dict):
    """Plot intersection markers on the axis."""
    if not points:
        return

    marker_color = (theme["text_primary"]
                    if theme["name"] == "dark"
                    else theme["text_primary"])

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    ax.scatter(
        xs, ys,
        s=config.INTERSECT["marker_size"] ** 2,
        color=marker_color,
        zorder=6,
        edgecolors=theme["accent_primary"],
        linewidths=1.5,
    )

    for x, y in points:
        ax.annotate(
            f"({x:.2f}, {y:.2f})",
            xy=(x, y),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=7,
            color=theme["text_secondary"],
            zorder=7,
        )