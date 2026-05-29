# ui/graph_panel.py — Graph canvas panel
#
# Owns the Matplotlib Figure/Axes, zoom/pan state, control bar,
# coordinate tracker label, and wires up mouse events for tracer + pan.

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import config
from config import (
    FONTS, ZOOM_DEFAULT, ZOOM_MIN, ZOOM_MAX,
    ZOOM_IN_FACTOR, ZOOM_OUT_FACTOR,
    ZOOM_SCROLL_IN, ZOOM_SCROLL_OUT,
    RENDER,
)
from renderer import style_axis, render_equation
from intersection import find_intersections, draw_intersections
from tracer import TracerOverlay, get_snap_point


class GraphPanel:
    """
    Center panel containing the Matplotlib canvas and all graph controls.
    The host (layout.py) calls plot_all() to re-render every equation.
    """

    def __init__(self, parent, theme: dict):
        self.theme      = theme
        self.zoom       = ZOOM_DEFAULT
        self.show_grid  = True
        self._pan_start = None   # (x_data, y_data) at mouse-press for panning
        self._pan_origin_lim = None
        self._tracer    = TracerOverlay()
        self._tracer_active_row = None   # EquationRow to trace (or None = all)

        # ── Root frame ────────────────────────────────────────────────────────
        self.frame = tk.Frame(parent, bg=theme["graph_fg"], padx=8, pady=8)
        self.frame.grid(row=0, column=1, sticky="nsew")
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # ── Control bar ───────────────────────────────────────────────────────
        self._build_control_bar()

        # ── Matplotlib figure ─────────────────────────────────────────────────
        self.fig = Figure(figsize=(5, 4.8), dpi=100,
                          facecolor=theme["graph_fg"])
        self.ax  = self.fig.add_subplot(111)
        style_axis(self.ax, self.fig, self.zoom, self.theme, self.show_grid)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(
            row=1, column=0, sticky="nsew", pady=(4, 0)
        )

        # ── Coordinate tracker ─────────────────────────────────────────────
        self.tracker = tk.Label(
            self.frame,
            text="x: —  |  y: —",
            font=FONTS["tracker"],
            bg=theme["tracker_bg"],
            fg=theme["text_muted"],
            pady=4,
        )
        self.tracker.grid(row=2, column=0, sticky="ew")

        # ── Mouse bindings ────────────────────────────────────────────────────
        cw = self.canvas.get_tk_widget()
        cw.bind("<MouseWheel>",   self._on_scroll)
        cw.bind("<Button-4>",     self._on_scroll)
        cw.bind("<Button-5>",     self._on_scroll)
        cw.bind("<ButtonPress-2>",   self._on_pan_start)
        cw.bind("<B2-Motion>",       self._on_pan_move)
        cw.bind("<ButtonRelease-2>", self._on_pan_end)

        self.fig.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.fig.canvas.mpl_connect("axes_leave_event",    self._on_mouse_leave)

        # Debounce timer id
        self._debounce_id = None
        # Stored equation rows for re-render
        self._eq_rows = []
        self._show_intersections = True

    # ── Public API ────────────────────────────────────────────────────────────

    def plot_all(self, equation_rows, show_intersections: bool = True,
                 show_grid: bool = True, resolution: int | None = None):
        """Full re-render. Called by layout on any equation change."""
        self._eq_rows            = equation_rows
        self._show_intersections = show_intersections
        self.show_grid           = show_grid

        res = resolution or RENDER["high_res"]
        self._render(res)

    def schedule_render(self, equation_rows, show_intersections: bool,
                        show_grid: bool):
        """
        Debounced render: draw low-res immediately, then schedule high-res
        after RENDER["debounce_ms"] ms of inactivity.
        """
        self._eq_rows            = equation_rows
        self._show_intersections = show_intersections
        self.show_grid           = show_grid

        # Immediate low-res pass
        self._render(RENDER["low_res"])

        # Cancel previous high-res timer
        if self._debounce_id:
            self.frame.after_cancel(self._debounce_id)
        self._debounce_id = self.frame.after(
            RENDER["debounce_ms"],
            lambda: self._render(RENDER["high_res"]),
        )

    def set_tracer_row(self, row):
        """Set which equation row the tracer snaps to (None = closest of all)."""
        self._tracer_active_row = row

    def set_theme(self, theme: dict):
        self.theme = theme
        self.frame.config(bg=theme["graph_fg"])
        self._ctrl_bar.config(bg=theme["graph_fg"])
        self.tracker.config(
            bg=theme["tracker_bg"],
            fg=theme["text_muted"],
        )
        self.fig.set_facecolor(theme["graph_fg"])
        for btn, _ in self._ctrl_btns:
            btn.config(
                bg=theme["surface_bg"],
                fg=theme["text_primary"],
                activebackground=theme["card_bg"],
                activeforeground=theme["text_primary"],
            )
        self._zoom_lbl.config(
            bg=theme["surface_bg"],
            fg=theme["text_muted"],
        )
        self._render(RENDER["high_res"])

    def reset_zoom(self):
        self.zoom = ZOOM_DEFAULT
        self._render(RENDER["high_res"])

    # ── Control bar ───────────────────────────────────────────────────────────

    def _build_control_bar(self):
        self._ctrl_bar = tk.Frame(self.frame, bg=self.theme["graph_fg"])
        self._ctrl_bar.grid(row=0, column=0, sticky="ew")
        self._ctrl_btns = []

        controls = [
            ("＋ Zoom In",  lambda: self._zoom(ZOOM_IN_FACTOR)),
            ("－ Zoom Out", lambda: self._zoom(ZOOM_OUT_FACTOR)),
            ("⟳ Reset",    self.reset_zoom),
            ("⊞ Grid",     self._toggle_grid),
        ]
        for label, cmd in controls:
            btn = tk.Button(
                self._ctrl_bar,
                text=label,
                font=FONTS["btn_small"],
                bg=self.theme["surface_bg"],
                fg=self.theme["text_primary"],
                bd=0,
                padx=8, pady=4,
                relief="flat",
                cursor="hand2",
                command=cmd,
                activebackground=self.theme["card_bg"],
                activeforeground=self.theme["text_primary"],
            )
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self._ctrl_btns.append((btn, label))

        # Zoom readout
        self._zoom_lbl = tk.Label(
            self._ctrl_bar,
            text=f"±{self.zoom:.1f}",
            font=FONTS["label_sm"],
            bg=self.theme["surface_bg"],
            fg=self.theme["text_muted"],
        )
        self._zoom_lbl.pack(side=tk.LEFT, padx=6)

    # ── Internal render ───────────────────────────────────────────────────────

    def _render(self, resolution: int):
        style_axis(self.ax, self.fig, self.zoom, self.theme, self.show_grid)

        visible_rows = [r for r in self._eq_rows if r.visible]

        for row in visible_rows:
            raw = row.get_text()
            if not raw:
                continue
            ok = render_equation(
                self.ax, raw, row.color, self.zoom, resolution, self.theme
            )
            row.set_valid(ok)

        # Intersection overlay
        if self._show_intersections and len(visible_rows) >= 2:
            all_pts = []
            rows = visible_rows
            for i in range(len(rows)):
                for j in range(i + 1, len(rows)):
                    pts = find_intersections(
                        rows[i].get_text(),
                        rows[j].get_text(),
                        self.zoom,
                    )
                    all_pts.extend(pts)
            draw_intersections(self.ax, all_pts, self.theme)

        self._zoom_lbl.config(text=f"±{self.zoom:.1f}")
        self.canvas.draw_idle()

    # ── Zoom ──────────────────────────────────────────────────────────────────

    def _zoom(self, factor: float):
        new_zoom = self.zoom * factor
        self.zoom = max(ZOOM_MIN, min(ZOOM_MAX, new_zoom))
        self._render(RENDER["high_res"])

    def _toggle_grid(self):
        self.show_grid = not self.show_grid
        self._render(RENDER["high_res"])

    # ── Mouse scroll zoom ─────────────────────────────────────────────────────

    def _on_scroll(self, event):
        # Linux: Button-4 = up (zoom in), Button-5 = down (zoom out)
        if hasattr(event, "num"):
            factor = ZOOM_SCROLL_IN if event.num == 4 else ZOOM_SCROLL_OUT
        else:
            factor = ZOOM_SCROLL_IN if event.delta > 0 else ZOOM_SCROLL_OUT
        self._zoom(factor)

    # ── Middle-mouse pan ──────────────────────────────────────────────────────

    def _on_pan_start(self, event):
        # Convert pixel → data coords
        inv = self.ax.transData.inverted()
        x_d, y_d = inv.transform((event.x, event.y))
        self._pan_start = (x_d, y_d)
        self._pan_origin_lim = (
            self.ax.get_xlim(),
            self.ax.get_ylim(),
        )

    def _on_pan_move(self, event):
        if self._pan_start is None:
            return
        inv = self.ax.transData.inverted()
        x_d, y_d = inv.transform((event.x, event.y))
        dx = self._pan_start[0] - x_d
        dy = self._pan_start[1] - y_d
        xl0, xl1 = self._pan_origin_lim[0]
        yl0, yl1 = self._pan_origin_lim[1]
        self.ax.set_xlim(xl0 + dx, xl1 + dx)
        self.ax.set_ylim(yl0 + dy, yl1 + dy)
        self.canvas.draw_idle()

    def _on_pan_end(self, event):
        self._pan_start = None
        self._pan_origin_lim = None

    # ── Mouse-move: tracer + coordinate display ───────────────────────────────

    def _on_mouse_move(self, event):
        if event.inaxes != self.ax:
            return

        mx, my = event.xdata, event.ydata
        if mx is None or my is None:
            return

        # Update coordinate tracker
        self.tracker.config(
            text=f"x: {mx:.3f}   y: {my:.3f}",
            fg=self.theme["tracker_fg"],
        )

        # Tracer: find snap point on focused row (or closest visible row)
        snap_pt    = None
        snap_color = self.theme["accent_primary"]

        rows_to_check = (
            [self._tracer_active_row]
            if self._tracer_active_row and self._tracer_active_row.visible
            else [r for r in self._eq_rows if r.visible]
        )

        for row in rows_to_check:
            raw = row.get_text()
            if not raw:
                continue
            pt = get_snap_point(raw, mx, my, self.zoom)
            if pt is not None:
                snap_pt    = pt
                snap_color = row.color
                break

        self._tracer.update(self.ax, snap_pt, snap_color, self.theme)
        self.canvas.draw_idle()

    def _on_mouse_leave(self, event):
        self._tracer.clear(self.ax)
        self.tracker.config(
            text="x: —  |  y: —",
            fg=self.theme["text_muted"],
        )
        self.canvas.draw_idle()