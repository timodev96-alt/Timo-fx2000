# ui/layout.py — Root layout, theme controller, event wiring

import tkinter as tk
from tkinter import ttk
import config
from config import (
    APP_TITLE, APP_GEOMETRY, APP_MIN_SIZE, LAYOUT_COLS,
    THEMES, FONTS, RENDER, EQ_MODE_STANDARD,
)
from ui.keypad      import KeypadPanel
from ui.graph_panel import GraphPanel
from ui.sidebar     import SidebarPanel


class AppLayout:
    """
    Top-level layout controller.
    Row 0 = custom frameless title bar.
    Row 1 = three-column content (keypad | graph | sidebar).
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._theme_name = "dark"
        self.theme = THEMES[self._theme_name]
        self._drag_x = self._drag_y = 0
        self._maximised = False
        self._pre_max_geometry = APP_GEOMETRY

        self._configure_root()
        self._apply_ttk_style()
        self._build_panels()
        self._seed_equations()

    # ── Root window ───────────────────────────────────────────────────────────

    def _configure_root(self):
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        self.root.minsize(*APP_MIN_SIZE)
        self.root.configure(bg=self.theme["app_bg"])
        self.root.resizable(True, True)

        # Remove the native OS title bar
        self.root.overrideredirect(True)

        # Row 0 = custom title bar (fixed height), Row 1 = content
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=0,
                                  minsize=LAYOUT_COLS["keypad"]["minsize"])
        self.root.columnconfigure(1, weight=1,
                                  minsize=LAYOUT_COLS["graph"]["minsize"])
        self.root.columnconfigure(2, weight=0,
                                  minsize=LAYOUT_COLS["sidebar"]["minsize"])

        # ── Custom title bar ──────────────────────────────────────────────────
        self._title_bar = tk.Frame(
            self.root,
            bg=self.theme["surface_bg"],
            height=34,
        )
        self._title_bar.grid(row=0, column=0, columnspan=3, sticky="ew")
        self._title_bar.columnconfigure(1, weight=1)
        self._title_bar.grid_propagate(False)

        # App name / icon
        self._title_lbl = tk.Label(
            self._title_bar,
            text="  📈  " + APP_TITLE,
            font=FONTS["subhead"],
            bg=self.theme["surface_bg"],
            fg=self.theme["text_primary"],
        )
        self._title_lbl.grid(row=0, column=0, sticky="w", padx=(8, 0))

        # Right-side controls frame
        self._ctrl_frame = tk.Frame(self._title_bar, bg=self.theme["surface_bg"])
        self._ctrl_frame.grid(row=0, column=2, sticky="e", padx=(0, 4))

        self._theme_btn = tk.Button(
            self._ctrl_frame,
            text="☀  Light",
            font=FONTS["label_sm"],
            bg=self.theme["surface_bg"],
            fg=self.theme["text_secondary"],
            bd=0, padx=10, pady=6,
            cursor="hand2", relief="flat",
            activebackground=self.theme["card_bg"],
            activeforeground=self.theme["text_primary"],
            command=self._toggle_theme,
        )
        self._theme_btn.pack(side=tk.LEFT)

        self._min_btn = tk.Button(
            self._ctrl_frame,
            text=" ─ ",
            font=FONTS["label_sm"],
            bg=self.theme["surface_bg"],
            fg=self.theme["text_secondary"],
            bd=0, padx=10, pady=6,
            cursor="hand2", relief="flat",
            activebackground=self.theme["card_bg"],
            activeforeground=self.theme["text_primary"],
            command=lambda: self.root.iconify(),
        )
        self._min_btn.pack(side=tk.LEFT)

        self._max_btn = tk.Button(
            self._ctrl_frame,
            text=" ▢ ",
            font=FONTS["label_sm"],
            bg=self.theme["surface_bg"],
            fg=self.theme["text_secondary"],
            bd=0, padx=10, pady=6,
            cursor="hand2", relief="flat",
            activebackground=self.theme["card_bg"],
            activeforeground=self.theme["text_primary"],
            command=self._on_maximise_toggle,
        )
        self._max_btn.pack(side=tk.LEFT)

        self._close_btn = tk.Button(
            self._ctrl_frame,
            text=" ✕ ",
            font=FONTS["label_sm"],
            bg=self.theme["surface_bg"],
            fg=self.theme["accent_danger"],
            bd=0, padx=10, pady=6,
            cursor="hand2", relief="flat",
            activebackground="#3a1a1a",
            activeforeground=self.theme["accent_danger"],
            command=self.root.destroy,
        )
        self._close_btn.pack(side=tk.LEFT)

        # Drag bindings — attach to bar AND its label so entire bar drags
        for widget in (self._title_bar, self._title_lbl):
            widget.bind("<ButtonPress-1>",  self._on_drag_start)
            widget.bind("<B1-Motion>",      self._on_drag_move)
            widget.bind("<Double-Button-1>",self._on_maximise_toggle)

    # ── TTK style ─────────────────────────────────────────────────────────────

    def _apply_ttk_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Vertical.TScrollbar",
            background=self.theme["surface_bg"],
            troughcolor=self.theme["panel_bg"],
            bordercolor=self.theme["panel_bg"],
            arrowcolor=self.theme["text_muted"],
            relief="flat",
        )

    # ── Panel construction ────────────────────────────────────────────────────

    def _build_panels(self):
        self.keypad  = KeypadPanel(
            self.root, self.theme,
            on_button=self._on_keypad_button,
        )
        self.graph   = GraphPanel(self.root, self.theme)
        self.sidebar = SidebarPanel(
            self.root, self.theme,
            on_equations_changed=self._on_equations_changed,
            on_focus_row=self._on_focus_row,
        )
        # Place all content panels on row 1 (row 0 = title bar)
        self.keypad.frame.grid( row=1, column=0, sticky="nsew")
        self.graph.frame.grid(  row=1, column=1, sticky="nsew")
        self.sidebar.frame.grid(row=1, column=2, sticky="nsew")

    def _seed_equations(self):
        self.sidebar.add_row("((x/6.5)^2 + (y/6.5)^2 - 1)^3 - (x/6.5)^2 * (y/6.5)^3 = 0")
        if self.sidebar.equation_rows:
            self.sidebar.set_active_row(self.sidebar.equation_rows[0])
        self._full_render()

    # ── Drag to move ──────────────────────────────────────────────────────────

    def _on_drag_start(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _on_drag_move(self, event):
        if self._maximised:
            return
        self.root.geometry(
            f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}"
        )

    def _on_maximise_toggle(self, event=None):
        if self._maximised:
            self.root.geometry(self._pre_max_geometry)
            self._maximised = False
        else:
            self._pre_max_geometry = self.root.geometry()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh}+0+0")
            self._maximised = True

    # ── Key event handlers ────────────────────────────────────────────────────

    def _on_keypad_button(self, token: str):
        row = self.sidebar.get_active_row()
        if row is None:
            return

        current = row.get_text()

        if token == "C":
            row.set_text("")
            self._full_render()
            return

        if token == "DEL":
            if current:
                row.set_text(current[:-1])
            self._schedule_render()
            return

        if token == "GRAPH":
            self._full_render()
            return

        if token == "()":
            opens  = current.count("(")
            closes = current.count(")")
            insert = "(" if opens <= closes else ")"
            row.set_text(current + insert)
            self._schedule_render()
            return

        row.set_text(current + token)
        self._schedule_render()
        row.focus()

    def _on_equations_changed(self):
        self._schedule_render()

    def _on_focus_row(self, row):
        self.graph.set_tracer_row(row)

    def _schedule_render(self):
        self.graph.schedule_render(
            self.sidebar.equation_rows,
            show_intersections=self.sidebar.show_intersections.get(),
            show_grid=self.graph.show_grid,
        )

    def _full_render(self):
        self.graph.plot_all(
            self.sidebar.equation_rows,
            show_intersections=self.sidebar.show_intersections.get(),
            show_grid=self.graph.show_grid,
        )

    # ── Theme toggle ──────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        self.theme = THEMES[self._theme_name]

        self.root.configure(bg=self.theme["app_bg"])

        # Restyle title bar widgets
        tb_bg = self.theme["surface_bg"]
        self._title_bar.config(bg=tb_bg)
        self._ctrl_frame.config(bg=tb_bg)
        self._title_lbl.config(bg=tb_bg, fg=self.theme["text_primary"])
        for btn in (self._theme_btn, self._min_btn, self._max_btn):
            btn.config(bg=tb_bg, fg=self.theme["text_secondary"],
                       activebackground=self.theme["card_bg"])
        self._close_btn.config(bg=tb_bg, fg=self.theme["accent_danger"])
        self._theme_btn.config(
            text="☀  Light" if self._theme_name == "dark" else "🌙  Dark"
        )

        self._apply_ttk_style()
        self.keypad.set_theme(self.theme)
        self.graph.set_theme(self.theme)
        self.sidebar.set_theme(self.theme)
