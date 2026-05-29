# ui/sidebar.py — Equation manager sidebar

import tkinter as tk
from tkinter import ttk
import config
from config import (
    COLOR_PALETTE, FONTS, EQ_MODE_STANDARD, EQ_MODE_PARAMETRIC,
    EQ_MODE_TANGENT, EQ_MODE_LABELS,
)


class EquationRow:
    """One equation entry card in the sidebar."""

    def __init__(self, parent_frame, index: int, color: str,
                 theme: dict, on_change, on_delete, on_focus):
        self.index      = index
        self.color      = color
        self.theme      = theme
        self.mode       = EQ_MODE_STANDARD
        self.visible    = True
        self._on_change = on_change
        self._on_delete = on_delete
        self._on_focus  = on_focus

        # ── Card frame ────────────────────────────────────────────────────────
        self.frame = tk.Frame(
            parent_frame,
            bg=theme["card_bg"],
            pady=5, padx=8,
            highlightthickness=1,
            highlightbackground=theme["border"],
        )
        self.frame.pack(fill=tk.X, pady=3, padx=2)
        self.frame.columnconfigure(1, weight=1)

        # ── Color swatch ─────────────────────────────────────────────────────
        self.swatch = tk.Label(
            self.frame, text="  ",
            bg=color, width=2, cursor="hand2",
        )
        self.swatch.grid(row=0, column=0, rowspan=2, padx=(0, 8), sticky="ns")
        self.swatch.bind("<Button-1>", lambda e: self._cycle_color())

        # ── Top row ───────────────────────────────────────────────────────────
        self._top = tk.Frame(self.frame, bg=theme["card_bg"])
        self._top.grid(row=0, column=1, sticky="ew")
        self._top.columnconfigure(0, weight=1)

        self.label = tk.Label(
            self._top, text=f"EQ {index + 1}",
            font=FONTS["label_sm"],
            bg=theme["card_bg"], fg=color,
        )
        self.label.grid(row=0, column=0, sticky="w")

        self.mode_btn = tk.Button(
            self._top, text=EQ_MODE_LABELS[self.mode],
            font=("Courier New", 8, "bold"),
            bg=theme["surface_bg"], fg=theme["text_secondary"],
            bd=0, padx=4, pady=1, cursor="hand2",
            activebackground=theme["border"],
            activeforeground=theme["text_primary"],
            command=self._cycle_mode,
        )
        self.mode_btn.grid(row=0, column=1, padx=(4, 2))

        self.vis_btn = tk.Button(
            self._top, text="●",
            font=("Helvetica Neue", 10),
            bg=theme["card_bg"], fg=color,
            bd=0, padx=2, pady=0, cursor="hand2",
            activebackground=theme["card_bg"],
            command=self._toggle_visibility,
        )
        self.vis_btn.grid(row=0, column=2, padx=(2, 2))

        self._del_btn = tk.Button(
            self._top, text="✕",
            font=("Helvetica Neue", 10, "bold"),
            bg=theme["card_bg"], fg=theme["accent_danger"],
            bd=0, padx=4, pady=0, cursor="hand2",
            activebackground=theme["card_bg"],
            activeforeground=theme["accent_danger"],
            command=lambda: self._on_delete(self),
        )
        self._del_btn.grid(row=0, column=3)

        # ── Entry row ─────────────────────────────────────────────────────────
        self._bottom = tk.Frame(self.frame, bg=theme["card_bg"])
        self._bottom.grid(row=1, column=1, sticky="ew", pady=(3, 0))
        self._bottom.columnconfigure(0, weight=1)

        self.entry = tk.Entry(
            self._bottom,
            font=FONTS["eq_entry"],
            bg=theme["entry_bg"], fg=theme["entry_fg"],
            bd=0, insertbackground=theme["accent_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme["border"],
            highlightcolor=color,
        )
        self.entry.grid(row=0, column=0, sticky="ew", ipady=4)
        self.entry.bind("<Button-1>", lambda e: self._on_focus(self))
        self.entry.bind("<KeyRelease>", lambda e: self._on_change(self))

        self.valid_dot = tk.Label(
            self._bottom, text="●",
            font=("Helvetica Neue", 10),
            bg=theme["card_bg"], fg=theme["text_muted"],
        )
        self.valid_dot.grid(row=0, column=1, padx=(4, 0))

        self.hint_lbl = tk.Label(
            self.frame, text="",
            font=FONTS["label_sm"],
            bg=theme["card_bg"], fg=theme["text_muted"],
        )
        self.hint_lbl.grid(row=2, column=1, sticky="w", pady=(2, 0))

    # ── Public API ────────────────────────────────────────────────────────────

    def get_text(self) -> str:
        return self.entry.get().strip()

    def set_text(self, text: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)

    def focus(self):
        self.entry.focus_set()

    def set_valid(self, ok: bool):
        self.valid_dot.config(
            fg=self.theme["accent_success"] if ok else self.theme["accent_danger"]
        )

    def set_theme(self, theme: dict):
        self.theme = theme
        # Card
        self.frame.config(bg=theme["card_bg"],
                          highlightbackground=theme["border"])
        # All internal frames
        for f in (self._top, self._bottom):
            f.config(bg=theme["card_bg"])
        # Labels
        self.label.config(bg=theme["card_bg"], fg=self.color)
        self.hint_lbl.config(bg=theme["card_bg"], fg=theme["text_muted"])
        self.valid_dot.config(bg=theme["card_bg"])
        # Buttons
        self.mode_btn.config(
            bg=theme["surface_bg"], fg=theme["text_secondary"],
            activebackground=theme["border"],
            activeforeground=theme["text_primary"],
        )
        self.vis_btn.config(
            bg=theme["card_bg"], activebackground=theme["card_bg"],
            fg=self.color if self.visible else theme["text_muted"],
        )
        self._del_btn.config(
            bg=theme["card_bg"], activebackground=theme["card_bg"],
            fg=theme["accent_danger"],
        )
        # Entry
        self.entry.config(
            bg=theme["entry_bg"], fg=theme["entry_fg"],
            insertbackground=theme["accent_primary"],
            highlightbackground=theme["border"],
            highlightcolor=self.color,
        )

    def renumber(self, new_index: int):
        self.index = new_index
        self.label.config(text=f"EQ {new_index + 1}")

    # ── Private ───────────────────────────────────────────────────────────────

    def _cycle_mode(self):
        modes = [EQ_MODE_STANDARD, EQ_MODE_PARAMETRIC, EQ_MODE_TANGENT]
        self.mode = modes[(modes.index(self.mode) + 1) % len(modes)]
        self.mode_btn.config(text=EQ_MODE_LABELS[self.mode])
        hints = {
            EQ_MODE_STANDARD:   "",
            EQ_MODE_PARAMETRIC: "x=cos(t), y=sin(t)",
            EQ_MODE_TANGENT:    "y=x^2 @ x=1",
        }
        self.hint_lbl.config(text=hints[self.mode])
        self._on_change(self)

    def _toggle_visibility(self):
        self.visible = not self.visible
        self.vis_btn.config(
            fg=self.color if self.visible else self.theme["text_muted"]
        )
        self._on_change(self)

    def _cycle_color(self):
        idx = COLOR_PALETTE.index(self.color) if self.color in COLOR_PALETTE else 0
        self.color = COLOR_PALETTE[(idx + 1) % len(COLOR_PALETTE)]
        self.swatch.config(bg=self.color)
        self.label.config(fg=self.color)
        self.vis_btn.config(fg=self.color if self.visible else self.theme["text_muted"])
        self.entry.config(highlightcolor=self.color)
        self._on_change(self)


# ── Sidebar panel ─────────────────────────────────────────────────────────────

class SidebarPanel:

    def __init__(self, parent, theme: dict, on_equations_changed, on_focus_row):
        self.theme                = theme
        self.on_equations_changed = on_equations_changed
        self.on_focus_row         = on_focus_row
        self.equation_rows: list[EquationRow] = []
        self.active_row: EquationRow | None   = None
        self.show_intersections = tk.BooleanVar(value=True)

        # ── Root frame ────────────────────────────────────────────────────────
        self.frame = tk.Frame(parent, bg=theme["panel_bg"], padx=12, pady=10)
        self.frame.grid(row=0, column=2, sticky="nsew")
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────────────
        self._header_frame = tk.Frame(self.frame, bg=theme["panel_bg"])
        self._header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self._header_frame.columnconfigure(0, weight=1)

        self._header_lbl = tk.Label(
            self._header_frame, text="EQUATIONS",
            font=FONTS["heading"],
            bg=theme["panel_bg"], fg=theme["text_primary"],
        )
        self._header_lbl.grid(row=0, column=0, sticky="w")

        self._opts_frame = tk.Frame(self._header_frame, bg=theme["panel_bg"])
        self._opts_frame.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self._cb_intersect = self._make_checkbox(
            self._opts_frame, "Intersections", self.show_intersections, 0
        )

        # ── Scrollable list ───────────────────────────────────────────────────
        self._list_container = tk.Frame(self.frame, bg=theme["panel_bg"])
        self._list_container.grid(row=1, column=0, sticky="nsew")
        self._list_container.rowconfigure(0, weight=1)
        self._list_container.columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(
            self._list_container, bg=theme["panel_bg"],
            bd=0, highlightthickness=0,
        )
        self._scrollbar = ttk.Scrollbar(
            self._list_container, orient="vertical",
            command=self._canvas.yview,
        )
        self._scrollable = tk.Frame(self._canvas, bg=theme["panel_bg"])
        self._scrollable.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            ),
        )
        self._canvas.create_window((0, 0), window=self._scrollable, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._scrollbar.grid(row=0, column=1, sticky="ns")

        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self._canvas.bind_all("<Button-5>",   self._on_mousewheel)

        # ── Footer ────────────────────────────────────────────────────────────
        self._footer_frame = tk.Frame(self.frame, bg=theme["panel_bg"])
        self._footer_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self._footer_frame.columnconfigure(0, weight=1)

        self._add_btn = tk.Button(
            self._footer_frame,
            text="＋  Add Equation",
            font=FONTS["btn_small"],
            bg=theme["accent_primary"], fg="#ffffff",
            bd=0, padx=8, pady=6,
            cursor="hand2", relief="flat",
            activebackground=theme["accent_primary"],
            activeforeground="#ffffff",
            command=lambda: self.add_row(),
        )
        self._add_btn.grid(row=0, column=0, sticky="ew")

        self.status_lbl = tk.Label(
            self._footer_frame, text="",
            font=FONTS["label_sm"],
            bg=theme["panel_bg"], fg=theme["text_muted"],
        )
        self.status_lbl.grid(row=1, column=0, sticky="w", pady=(4, 0))

    # ── Public API ────────────────────────────────────────────────────────────

    def add_row(self, initial_text: str = "",
                mode: str = EQ_MODE_STANDARD) -> EquationRow:
        idx   = len(self.equation_rows)
        color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
        row   = EquationRow(
            self._scrollable, idx, color, self.theme,
            on_change=self._on_row_changed,
            on_delete=self._on_row_deleted,
            on_focus=self._on_row_focused,
        )
        row.set_text(initial_text)
        row.mode = mode
        self.equation_rows.append(row)
        self.set_active_row(row)
        self._scroll_to_bottom()
        return row

    def set_active_row(self, row: EquationRow):
        self.active_row = row
        row.focus()
        self.on_focus_row(row)

    def get_active_row(self) -> EquationRow | None:
        return self.active_row

    def set_theme(self, theme: dict):
        self.theme = theme

        # ── Top-level panel frames ────────────────────────────────────────────
        for widget in (self.frame, self._header_frame, self._opts_frame,
                       self._list_container, self._footer_frame, self._scrollable):
            widget.config(bg=theme["panel_bg"])
        self._canvas.config(bg=theme["panel_bg"])

        # ── Header labels ─────────────────────────────────────────────────────
        self._header_lbl.config(bg=theme["panel_bg"], fg=theme["text_primary"])
        self.status_lbl.config(bg=theme["panel_bg"], fg=theme["text_muted"])

        # ── Rebuild checkbox cleanly ──────────────────────────────────────────
        self._cb_intersect.destroy()
        self._cb_intersect = self._make_checkbox(
            self._opts_frame, "Intersections", self.show_intersections, 0
        )

        # ── Add button ────────────────────────────────────────────────────────
        self._add_btn.config(
            bg=theme["accent_primary"],
            activebackground=theme["accent_primary"],
        )

        # ── Equation rows ─────────────────────────────────────────────────────
        for row in self.equation_rows:
            row.set_theme(theme)

        # ── TTK scrollbar ─────────────────────────────────────────────────────
        style = ttk.Style()
        style.configure(
            "Vertical.TScrollbar",
            background=theme["surface_bg"],
            troughcolor=theme["panel_bg"],
            bordercolor=theme["panel_bg"],
            arrowcolor=theme["text_muted"],
        )

    def set_status(self, text: str):
        self.status_lbl.config(text=text)

    # ── Private ───────────────────────────────────────────────────────────────

    def _make_checkbox(self, parent, label: str,
                       var: tk.BooleanVar, col: int) -> tk.Checkbutton:
        cb = tk.Checkbutton(
            parent, text=label,
            variable=var,
            font=FONTS["label_sm"],
            bg=self.theme["panel_bg"],
            fg=self.theme["text_secondary"],
            selectcolor=self.theme["entry_bg"],
            activebackground=self.theme["panel_bg"],
            activeforeground=self.theme["text_primary"],
            bd=0,
            command=self.on_equations_changed,
        )
        cb.grid(row=0, column=col, padx=(0, 10), sticky="w")
        return cb

    def _on_row_changed(self, row):
        self.on_equations_changed()

    def _on_row_deleted(self, row):
        if len(self.equation_rows) <= 1:
            return
        self.equation_rows.remove(row)
        row.frame.destroy()
        for i, r in enumerate(self.equation_rows):
            r.renumber(i)
        if self.equation_rows:
            self.set_active_row(self.equation_rows[-1])
        self.on_equations_changed()

    def _on_row_focused(self, row):
        self.active_row = row
        self.on_focus_row(row)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_to_bottom(self):
        self._canvas.update_idletasks()
        self._canvas.yview_moveto(1.0)