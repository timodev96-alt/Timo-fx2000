APP_TITLE = "Timo F(x) 2000"
APP_GEOMETRY = "1400x700"
APP_RESIZABLE = (True, True)
APP_MIN_SIZE = (1100, 600)

LAYOUT_COLS = {
    "keypad":  {"weight": 0, "minsize": 390},
    "graph":   {"weight": 1, "minsize": 480},
    "sidebar": {"weight": 0, "minsize": 340},
}

# ── Equation color palette ────────────────────────────────────────────────────
COLOR_PALETTE = [
    "#e05c5c",  # red
    "#5cb8ff",  # sky blue
    "#5ce87e",  # mint green
    "#f5a623",  # amber
    "#b97ff5",  # violet
    "#f56ad0",  # pink
    "#5ef5e0",  # teal
    "#f5e25e",  # yellow
]

# ── Themes ────────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "name": "dark",
        "app_bg":            "#111318",
        "panel_bg":          "#1a1d24",
        "card_bg":           "#22262f",
        "surface_bg":        "#2a2f3b",
        "border":            "#353a48",
        "text_primary":      "#eaedf5",
        "text_secondary":    "#8891a8",
        "text_muted":        "#555e72",
        "accent_primary":    "#4f8ef7",
        "accent_success":    "#4ecb87",
        "accent_danger":     "#e05c5c",
        "accent_warning":    "#f5a623",
        "btn_number_bg":     "#22262f",
        "btn_number_fg":     "#eaedf5",
        "btn_op_bg":         "#2e3445",
        "btn_op_fg":         "#7fa8f7",
        "btn_fn_bg":         "#1e2c42",
        "btn_fn_fg":         "#5cb8ff",
        "btn_special_bg":    "#1e2a1e",
        "btn_special_fg":    "#4ecb87",
        "btn_clear_bg":      "#3a1a1a",
        "btn_clear_fg":      "#e05c5c",
        "btn_graph_bg":      "#1a3a1a",
        "btn_graph_fg":      "#4ecb87",
        "graph_bg":          "#0d0f14",
        "graph_fg":          "#1a1d24",
        "axis_color":        "#3a3f50",
        "grid_color":        "#1e2230",
        "axis_zero_color":   "#4a506a",
        "tracker_bg":        "#111318",
        "tracker_fg":        "#4ecb87",
        "entry_bg":          "#111318",
        "entry_fg":          "#eaedf5",
        "scrollbar_bg":      "#22262f",
        "tag_active_border": "#4f8ef7",
    },
    "light": {
        "name": "light",
        # ── Backgrounds ──────────────────────────────────────────────────────
        "app_bg":            "#e8eaf2",   # outer window bg
        "panel_bg":          "#f4f5fb",   # keypad + sidebar panels
        "card_bg":           "#ffffff",   # equation row cards
        "surface_bg":        "#dde0f0",   # title bar, button hover, surfaces
        "border":            "#c4c8e0",   # input highlight borders
        # ── Text ─────────────────────────────────────────────────────────────
        "text_primary":      "#12152a",   # headings, labels
        "text_secondary":    "#3d4468",   # secondary labels
        "text_muted":        "#8890b0",   # hints, placeholders
        # ── Accents ──────────────────────────────────────────────────────────
        "accent_primary":    "#2255d4",   # add-eq button, focus rings
        "accent_success":    "#15803d",   # graph button, valid dot
        "accent_danger":     "#c0152a",   # clear/delete/close
        "accent_warning":    "#b45309",
        # ── Keypad buttons ────────────────────────────────────────────────────
        "btn_number_bg":     "#ffffff",
        "btn_number_fg":     "#12152a",
        "btn_op_bg":         "#d6dcf5",
        "btn_op_fg":         "#1a3bbf",
        "btn_fn_bg":         "#cce0ff",
        "btn_fn_fg":         "#1440a8",
        "btn_special_bg":    "#c8f0d8",
        "btn_special_fg":    "#14532d",
        "btn_clear_bg":      "#fdd8d8",
        "btn_clear_fg":      "#991020",
        "btn_graph_bg":      "#bbf7d0",
        "btn_graph_fg":      "#14532d",
        # ── Graph canvas ─────────────────────────────────────────────────────
        "graph_bg":          "#f9faff",   # plot area fill
        "graph_fg":          "#eceef8",   # figure face (border around plot)
        "axis_color":        "#b0b6d4",   # spine lines
        "grid_color":        "#d8dcf0",   # grid lines
        "axis_zero_color":   "#8890b0",   # x=0 / y=0 lines
        # ── Tracker bar ──────────────────────────────────────────────────────
        "tracker_bg":        "#dde0f0",
        "tracker_fg":        "#15803d",
        # ── Sidebar / entry ───────────────────────────────────────────────────
        "entry_bg":          "#ffffff",
        "entry_fg":          "#12152a",
        "scrollbar_bg":      "#d6dcf5",
        "tag_active_border": "#2255d4",
    },
}

# ── Render settings ───────────────────────────────────────────────────────────
RENDER = {
    "low_res":           120,
    "high_res":          420,
    "debounce_ms":       380,
    "linewidth":         2.2,
    "tangent_linewidth": 1.6,
    "parametric_points": 3000,
    "t_range":           (-20, 20),
}

# ── Zoom ──────────────────────────────────────────────────────────────────────
ZOOM_DEFAULT    = 10.0
ZOOM_MIN        = 0.5
ZOOM_MAX        = 500.0
ZOOM_IN_FACTOR  = 0.6
ZOOM_OUT_FACTOR = 1.6
ZOOM_SCROLL_IN  = 0.88
ZOOM_SCROLL_OUT = 1.14

# ── Intersection detection ────────────────────────────────────────────────────
INTERSECT = {
    "grid_res":    80,
    "refine_iters": 30,
    "tolerance":   1e-7,
    "marker_size": 7,
    "marker_color_dark":  "#ffffff",
    "marker_color_light": "#111111",
}

# ── Tracer ────────────────────────────────────────────────────────────────────
TRACER = {
    "snap_radius":     0.6,
    "dot_size":        60,
    "dot_color_dark":  "#ffffff",
    "dot_color_light": "#111111",
    "label_offset":    (8, 8),
}

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONTS = {
    "heading":   ("Helvetica Neue", 13, "bold"),
    "subhead":   ("Helvetica Neue", 11, "bold"),
    "body":      ("Helvetica Neue", 11),
    "mono":      ("Courier New", 12, "bold"),
    "btn_main":  ("Helvetica Neue", 13, "bold"),
    "btn_small": ("Helvetica Neue", 11, "bold"),
    "eq_entry":  ("Courier New", 14),
    "tracker":   ("Courier New", 13, "bold"),
    "label_sm":  ("Helvetica Neue", 10),
}

# ── Equation row modes ────────────────────────────────────────────────────────
EQ_MODE_STANDARD   = "standard"
EQ_MODE_PARAMETRIC = "parametric"
EQ_MODE_TANGENT    = "tangent"

EQ_MODE_LABELS = {
    EQ_MODE_STANDARD:   "f(x,y)",
    EQ_MODE_PARAMETRIC: "param",
    EQ_MODE_TANGENT:    "tan",
}