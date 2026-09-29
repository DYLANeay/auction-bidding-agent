"""The monitor's colors, taken from the Tokyo Night theme for Neovim (think: the paint chart)"""

BACKGROUND = "#1a1b26"
BACKGROUND_DARK = "#16161e"
BACKGROUND_HIGHLIGHT = "#292e42"
BACKGROUND_ROW = "#1f2335"
SELECTION = "#283457"
BORDER = "#3b4261"
FOREGROUND = "#c0caf5"
FOREGROUND_DARK = "#a9b1d6"
COMMENT = "#565f89"
MUTED = "#737aa2"
BLUE = "#7aa2f7"
BLUE_DARK = "#3d59a1"
CYAN = "#7dcfff"
MAGENTA = "#bb9af7"
GREEN = "#9ece6a"
TEAL = "#73daca"
HINT = "#1abc9c"
YELLOW = "#e0af68"
ORANGE = "#ff9e64"
RED = "#f7768e"
RED_DARK = "#db4b4b"

GRADE_COLORS = {
    "A": f"bold {GREEN}",
    "B": TEAL,
    "C": YELLOW,
    "D": ORANGE,
    "E": RED,
    "F": f"bold {RED_DARK}",
}

# séparateurs de lualine (police Nerd Font)
SEPARATOR_RIGHT = ""
SEPARATOR_LEFT = ""

CSS = f"""
Screen {{
    background: {BACKGROUND};
    layers: base;
}}

#tabline, #statusline {{
    height: 1;
    background: {BACKGROUND_DARK};
}}

#statusline-left {{ width: 1fr; }}
#statusline-right {{ width: auto; }}

#body {{
    height: 1fr;
    padding: 0 1;
}}

.panel {{
    background: {BACKGROUND};
    border: round {BORDER};
    border-title-color: {BLUE};
    border-title-style: bold;
    border-subtitle-color: {COMMENT};
    padding: 1 1 0 1;
}}

#agent-panel {{ width: 5fr; }}
#game-panel {{
    width: 6fr;
    border-title-color: {MAGENTA};
}}

.chart-label {{
    color: {COMMENT};
    margin-top: 1;
}}

Sparkline {{
    height: 1fr;
    min-height: 3;
    max-height: 12;
    background: {BACKGROUND};
}}

#market > .sparkline--min-color {{ color: {BLUE_DARK}; }}
#market > .sparkline--max-color {{ color: {CYAN}; }}
#gold > .sparkline--min-color {{ color: #3b5a3a; }}
#gold > .sparkline--max-color {{ color: {GREEN}; }}

#ranking {{
    height: 1fr;
    margin-top: 1;
    background: {BACKGROUND};
    scrollbar-size: 1 1;
}}

#ranking > .datatable--header {{
    background: {BACKGROUND_DARK};
    color: {BLUE};
    text-style: bold;
}}

#ranking > .datatable--odd-row {{ background: {BACKGROUND}; }}
#ranking > .datatable--even-row {{ background: {BACKGROUND_ROW}; }}

Toast {{
    background: {BACKGROUND_HIGHLIGHT};
    color: {FOREGROUND};
}}

.toast--title {{ color: {BLUE}; }}
"""
