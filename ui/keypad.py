import tkinter as tk
from config import FONTS
BUTTON_LAYOUT = [
    # Row 0 — top controls
    ("C",      "C",       "clear",   0, 0),
    ("( )",    "()",      "op",      0, 1),
    ("DEL",    "DEL",     "clear",   0, 2),
    ("GRAPH",  "GRAPH",   "graph",   0, 3),
    ("/",      "/",       "op",      0, 4),

    # Row 1 — trig
    ("sin",    "sin(",    "fn",      1, 0),
    ("7",      "7",       "number",  1, 1),
    ("8",      "8",       "number",  1, 2),
    ("9",      "9",       "number",  1, 3),
    ("×",      "*",       "op",      1, 4),

    # Row 2
    ("cos",    "cos(",    "fn",      2, 0),
    ("4",      "4",       "number",  2, 1),
    ("5",      "5",       "number",  2, 2),
    ("6",      "6",       "number",  2, 3),
    ("−",      "-",       "op",      2, 4),

    # Row 3
    ("tan",    "tan(",    "fn",      3, 0),
    ("1",      "1",       "number",  3, 1),
    ("2",      "2",       "number",  3, 2),
    ("3",      "3",       "number",  3, 3),
    ("+",      "+",       "op",      3, 4),

    # Row 4
    ("log",    "log(",    "fn",      4, 0),
    ("ln",     "ln(",     "fn",      4, 1),
    ("0",      "0",       "number",  4, 2),
    (".",      ".",       "number",  4, 3),
    ("=",      "=",       "op",      4, 4),

    # Row 5 — constants + special
    ("π",      "π",       "special", 5, 0),
    ("e",      "e",       "special", 5, 1),
    ("√(",     "√(",      "fn",      5, 2),
    ("^",      "^",       "op",      5, 3),
    ("x",      "x",       "special", 5, 4),

    # Row 6 — extra
    ("asin",   "asin(",   "fn",      6, 0),
    ("acos",   "acos(",   "fn",      6, 1),
    ("atan",   "atan(",   "fn",      6, 2),
    ("abs(",   "abs(",    "fn",      6, 3),
    ("y",      "y",       "special", 6, 4),
]


def _style_keys(style: str) -> tuple[str, str]:
    return f"btn_{style}_bg", f"btn_{style}_fg"


class KeypadPanel:
    def __init__(self, parent, theme: dict, on_button):
        self.theme     = theme
        self.on_button = on_button
        self._buttons  = []

        self.frame = tk.Frame(parent, bg=theme["panel_bg"], padx=10, pady=10)
        self.frame.grid(row=0, column=0, sticky="nsew")
        ROWS = 7
        COLS = 5
        for r in range(ROWS):
            self.frame.rowconfigure(r, weight=1, minsize=52)
        for c in range(COLS):
            self.frame.columnconfigure(c, weight=1, minsize=62)

        self._build_buttons()

    def _build_buttons(self):
        for label, token, style, row, col in BUTTON_LAYOUT:
            bg_key, fg_key = _style_keys(style)
            bg = self.theme.get(bg_key, self.theme["btn_number_bg"])
            fg = self.theme.get(fg_key, self.theme["btn_number_fg"])

            font = FONTS["btn_main"] if style in ("graph", "clear") else FONTS["btn_small"]

            btn = tk.Button(
                self.frame,
                text=label,
                font=font,
                bg=bg,
                fg=fg,
                bd=0,
                relief="flat",
                cursor="hand2",
                activebackground=self.theme["surface_bg"],
                activeforeground=self.theme["text_primary"],
                padx=4, pady=4,
                command=lambda t=token: self.on_button(t),
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            self._buttons.append((btn, style))

            btn.bind("<Enter>", lambda e, b=btn: b.config(
                bg=self.theme["surface_bg"]))
            btn.bind("<Leave>", lambda e, b=btn, s=style: b.config(
                bg=self.theme.get(f"btn_{s}_bg", self.theme["btn_number_bg"])))

    def set_theme(self, theme: dict):
        self.theme = theme
        self.frame.config(bg=theme["panel_bg"])
        for btn, style in self._buttons:
            bg_key, fg_key = _style_keys(style)
            bg = theme.get(bg_key, theme["btn_number_bg"])
            fg = theme.get(fg_key, theme["btn_number_fg"])
            btn.config(
                bg=bg, fg=fg,
                activebackground=theme["surface_bg"],
                activeforeground=theme["text_primary"],
            )
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=theme["surface_bg"]))
            btn.bind("<Leave>", lambda e, b=btn, s=style: b.config(
                bg=theme.get(f"btn_{s}_bg", theme["btn_number_bg"])))