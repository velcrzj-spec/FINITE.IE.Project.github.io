"""
FINITE - Your Very Own Financial Literacy Coach
Fostering Financial Literacy & Building Financial Awareness.

A pure-Python desktop UI prototype built with Tkinter + ttk.
No web technologies, no third-party packages.

Run:
    python finite_app.py

Screens
    Welcome  ->  User Setup  ->  Dashboard / Budget Allocation /
                                 Expense Tracker / Literacy Report

Code layout (top to bottom)
    1. Theme ............ colors, fonts, number formatting
    2. Drawing helpers .. rounded shapes, logo, icon glyphs
    3. Widgets .......... Card, RoundedButton, Field, Segmented, ProgressBar,
                          Ring, DonutChart, BarChart, ScrollFrame
    4. State ............ AppState (sample data + light arithmetic only)
    5. Screens .......... WelcomeScreen, SetupScreen
    6. Shell + pages .... Sidebar, Shell, Dashboard, Budget, Expenses, Report
    7. App .............. FiniteApp (navigation, toasts, transitions)
"""

import math
import tkinter as tk
import tkinter.font as tkfont
from datetime import date, datetime, time, timedelta
from tkinter import ttk


# =============================================================================
# 1. THEME
# =============================================================================

class C:
    """Color palette - one place to restyle the whole application."""
    BG = "#F3F5F9"            # app background
    SURFACE = "#FFFFFF"       # cards
    SURFACE_ALT = "#F7F9FC"   # inputs, table headers, inner panels
    BORDER = "#E2E8F0"
    SHADOW = "#E1E6EE"
    INK = "#0F172A"           # headings
    TEXT = "#1E293B"          # body text
    MUTED = "#64748B"
    SUBTLE = "#94A3B8"

    SIDEBAR = "#0B1628"
    SIDEBAR_2 = "#12223A"
    SIDEBAR_HOVER = "#15294A"
    SIDEBAR_TEXT = "#9FB0C8"

    PRIMARY = "#0EA371"       # FINITE emerald - growth & discipline
    PRIMARY_DARK = "#0A8058"
    PRIMARY_SOFT = "#E3F7EF"
    GOLD = "#F2B544"
    GOLD_SOFT = "#FFF7E6"

    NEEDS = "#3B6FF6"
    NEEDS_SOFT = "#E8EEFF"
    WANTS = "#F29A1F"
    WANTS_SOFT = "#FFF2DF"
    GOALS = "#0EA371"
    GOALS_SOFT = "#E3F7EF"
    DANGER = "#E5484D"
    DANGER_SOFT = "#FDECEC"


CATEGORY = {
    "Needs": {"color": C.NEEDS, "soft": C.NEEDS_SOFT,
              "desc": "Essentials you can't skip: meals, transport, school supplies."},
    "Wants": {"color": C.WANTS, "soft": C.WANTS_SOFT,
              "desc": "Lifestyle and leisure: snacks, milk tea, games, outings."},
    "Goals": {"color": C.GOALS, "soft": C.GOALS_SOFT,
              "desc": "Pay yourself first: protected savings you never spend."},
}


class Fonts:
    """Picks the best font family installed on this computer."""
    family = "Helvetica"
    mono = "Courier"
    _cache = {}

    @classmethod
    def init(cls, root):
        available = set(tkfont.families(root))
        for name in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter",
                     "Roboto", "Ubuntu", "Noto Sans", "DejaVu Sans", "Arial"):
            if name in available:
                cls.family = name
                break
        for name in ("Cascadia Mono", "Consolas", "SF Mono", "Menlo",
                     "DejaVu Sans Mono", "Noto Sans Mono", "Courier New"):
            if name in available:
                cls.mono = name
                break


def F(size, weight="normal"):
    """Font tuple. Negative size = pixels, so layouts look the same everywhere."""
    return (Fonts.family, -size, weight)


def measure(font, text):
    key = tuple(font)
    if key not in Fonts._cache:
        Fonts._cache[key] = tkfont.Font(family=font[0], size=font[1], weight=font[2])
    return Fonts._cache[key].measure(text)


def money(v):
    return f"-₱{abs(v):,.2f}" if v < 0 else f"₱{v:,.2f}"


def money_short(v):
    if abs(v) >= 1_000_000:
        return f"₱{v / 1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"₱{v / 1_000:.0f}k"
    return f"₱{v:,.0f}"


def nice_max(v):
    """Rounds a chart's top value up to a clean number (1, 2, 2.5, 5 x 10^n)."""
    if v <= 0:
        return 1
    exp = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if m * exp >= v:
            return m * exp
    return 10 * exp


def blend(c1, c2, t):
    """Mix two hex colors; t=0 gives c1, t=1 gives c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def greeting():
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


# =============================================================================
# 2. DRAWING HELPERS
# =============================================================================

def round_rect_points(x0, y0, x1, y1, r):
    r = max(0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    pts = []
    corners = ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0),
               (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180))
    for cx, cy, start in corners:
        for step in range(0, 91, 15):
            a = math.radians(start + step)
            pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
    return pts


def rounded_rect(canvas, x0, y0, x1, y1, r, **kw):
    kw.setdefault("outline", "")
    return canvas.create_polygon(round_rect_points(x0, y0, x1, y1, r), **kw)


def draw_logo(canvas, x, y, size, tags=()):
    """FINITE mark: emerald tile with three rising bars and a gold growth dot."""
    rounded_rect(canvas, x, y, x + size, y + size, size * 0.28, fill=C.PRIMARY, tags=tags)
    s = size / 40
    for i, hgt in enumerate((10, 16, 22)):
        bx = x + (9 + i * 8.5) * s
        canvas.create_rectangle(bx, y + (31 - hgt) * s, bx + 5.5 * s, y + 31 * s,
                                fill="#FFFFFF", outline="", tags=tags)
    canvas.create_oval(x + 29 * s, y + 5 * s, x + 35 * s, y + 11 * s,
                       fill=C.GOLD, outline="", tags=tags)


def draw_glyph(c, kind, cx, cy, color, w=2):
    """Simple line icons drawn on a canvas (no image files or emoji needed)."""
    if kind == "dashboard":
        for dx, dy in ((-8, -8), (1, -8), (-8, 1), (1, 1)):
            c.create_rectangle(cx + dx, cy + dy, cx + dx + 7, cy + dy + 7, outline=color, width=w)
    elif kind == "budget":
        c.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, outline=color, width=w)
        c.create_arc(cx - 8, cy - 8, cx + 8, cy + 8, start=90, extent=-115, fill=color, outline=color)
    elif kind == "expenses":
        for dy in (-6, 0, 6):
            c.create_oval(cx - 9, cy + dy - 1.5, cx - 6, cy + dy + 1.5, fill=color, outline=color)
            c.create_line(cx - 3, cy + dy, cx + 9, cy + dy, fill=color, width=w)
    elif kind == "report":
        for i, hgt in enumerate((7, 12, 17)):
            x = cx - 8 + i * 6
            c.create_rectangle(x, cy + 8 - hgt, x + 4, cy + 8, fill=color, outline="")
    elif kind == "setup":
        for dy, kx in ((-6, 3), (0, -4), (6, 1)):
            c.create_line(cx - 9, cy + dy, cx + 9, cy + dy, fill=color, width=w)
            c.create_oval(cx + kx - 3, cy + dy - 3, cx + kx + 3, cy + dy + 3, fill=C.SIDEBAR, outline=color, width=w)
    elif kind == "exit":
        c.create_line(cx - 2, cy - 8, cx - 8, cy - 8, cx - 8, cy + 8, cx - 2, cy + 8, fill=color, width=w)
        c.create_line(cx - 3, cy, cx + 9, cy, fill=color, width=w, arrow="last", arrowshape=(6, 7, 3))
    elif kind == "wallet":
        c.create_rectangle(cx - 9, cy - 7, cx + 9, cy + 7, outline=color, width=w)
        c.create_rectangle(cx + 2, cy - 2, cx + 9, cy + 3, fill=color, outline=color)
    elif kind == "trend":
        c.create_line(cx - 9, cy + 6, cx - 3, cy, cx + 1, cy + 4, cx + 9, cy - 5,
                      fill=color, width=w, arrow="last", arrowshape=(6, 7, 3))
    elif kind == "receipt":
        c.create_line(cx - 7, cy + 9, cx - 7, cy - 9, cx + 7, cy - 9, cx + 7, cy + 9,
                      cx + 4, cy + 6, cx + 1, cy + 9, cx - 2, cy + 6, cx - 4, cy + 9, cx - 7, cy + 6,
                      fill=color, width=w)
        for dy in (-4, 1):
            c.create_line(cx - 3, cy + dy, cx + 4, cy + dy, fill=color, width=w)
    elif kind == "shield":
        c.create_polygon(cx, cy - 9, cx + 8, cy - 6, cx + 7, cy + 3, cx, cy + 9, cx - 7, cy + 3, cx - 8, cy - 6,
                         outline=color, fill="", width=w)
        c.create_line(cx - 3, cy, cx - 1, cy + 3, cx + 4, cy - 3, fill=color, width=w)
    elif kind == "target":
        for r in (9, 5):
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=color, width=w)
        c.create_oval(cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5, fill=color, outline=color)
    elif kind == "clock":
        c.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, outline=color, width=w)
        c.create_line(cx, cy - 5, cx, cy, cx + 4, cy + 2, fill=color, width=w)
    elif kind == "bulb":
        c.create_oval(cx - 7, cy - 10, cx + 7, cy + 4, outline=color, width=w)
        c.create_line(cx - 3, cy + 7, cx + 3, cy + 7, fill=color, width=w)
        c.create_line(cx - 2, cy + 10, cx + 2, cy + 10, fill=color, width=w)
    elif kind == "plus":
        c.create_line(cx - 7, cy, cx + 7, cy, fill=color, width=w)
        c.create_line(cx, cy - 7, cx, cy + 7, fill=color, width=w)


def icon_badge(parent, kind, color, soft, size=40, radius=11):
    c = tk.Canvas(parent, width=size, height=size, bg=parent.cget("bg"), highlightthickness=0, bd=0)
    rounded_rect(c, 0, 0, size, size, radius, fill=soft)
    draw_glyph(c, kind, size / 2, size / 2, color)
    return c


def L(parent, text="", size=13, weight="normal", fg=None, **kw):
    """Label that automatically matches its parent's background."""
    kw.setdefault("bg", parent.cget("bg"))
    kw.setdefault("anchor", "w")
    kw.setdefault("justify", "left")
    return tk.Label(parent, text=text, font=F(size, weight), fg=fg or C.TEXT, **kw)


def wrap_label(parent, text, size=13, fg=None, weight="normal", **kw):
    """Label that re-wraps its text to the space it is given (pack with fill='x')."""
    lbl = L(parent, text, size, weight, fg, wraplength=300, **kw)
    lbl.bind("<Configure>", lambda e: lbl.configure(wraplength=max(60, e.width - 4)))
    return lbl


def divider(parent, pady=12, color=C.BORDER):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", pady=pady)


# =============================================================================
# 3. WIDGETS
# =============================================================================

class Card(tk.Canvas):
    """Rounded card with a soft drop shadow. Put content inside `card.body`."""

    def __init__(self, parent, padding=22, radius=16, fill=C.SURFACE, height=None,
                 width=None, shadow=False, border=C.BORDER):
        outer = parent.cget("bg")
        super().__init__(parent, bg=outer, highlightthickness=0, bd=0,
                         height=height or 20, width=width or 200)
        self.pad, self.radius, self.fill = padding, radius, fill
        self.fixed_height, self.border = height, border
        self.sh = 4 if shadow else 0
        self.body = tk.Frame(self, bg=fill)
        self._win = self.create_window(padding, padding, window=self.body, anchor="nw")
        self.bind("<Configure>", self._redraw)
        if not height:
            self.body.bind("<Configure>", self._fit, add="+")
            # the body is unmapped until the card is tall enough, so fit once content exists
            self.after_idle(self._fit)
            self.after(60, self._fit)

    def _fit(self, _=None):
        h = self.body.winfo_reqheight() + 2 * self.pad + self.sh
        if int(float(self.cget("height"))) != h:
            self.configure(height=h)

    def _redraw(self, _=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4 or h < 4:
            return
        self.delete("deco")
        if self.sh:
            rounded_rect(self, 0, self.sh, w, h, self.radius, fill=C.SHADOW, tags="deco")
        rounded_rect(self, 0, 0, w - 1, h - 1 - self.sh, self.radius, fill=self.fill,
                     outline=self.border or "", tags="deco")
        self.tag_lower("deco")
        self.itemconfigure(self._win, width=max(1, w - 2 * self.pad))
        if self.fixed_height:
            self.itemconfigure(self._win, height=max(1, h - 2 * self.pad - self.sh))


class RoundedButton(tk.Canvas):
    KINDS = {
        "primary": (C.PRIMARY, C.PRIMARY_DARK, "#FFFFFF", ""),
        "dark": (C.INK, "#1E293B", "#FFFFFF", ""),
        "ghost": (C.SURFACE, C.SURFACE_ALT, C.TEXT, C.BORDER),
        "soft": (C.PRIMARY_SOFT, "#CDEFE1", C.PRIMARY_DARK, ""),
        "danger": (C.DANGER_SOFT, "#FAD7D8", C.DANGER, ""),
    }

    def __init__(self, parent, text, command=None, kind="primary", width=None,
                 height=42, radius=10, size=13):
        self.fill, self.hover_fill, self.fg, self.outline = self.KINDS[kind]
        self.font = F(size, "bold")
        w = width or measure(self.font, text) + 40
        super().__init__(parent, width=w, height=height, bg=parent.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.text, self.command, self.radius, self._hover = text, command, radius, False
        self.bind("<Configure>", lambda e=None: self._draw())
        self.bind("<Enter>", lambda e=None: self._set_hover(True))
        self.bind("<Leave>", lambda e=None: self._set_hover(False))
        self.bind("<Button-1>", self._click)
        self._draw()

    def _set_hover(self, value):
        self._hover = value
        self._draw()

    def _click(self, _):
        if self.command:
            self.command()

    def _draw(self):
        w = max(self.winfo_width(), 2) if self.winfo_width() > 1 else int(self.cget("width"))
        h = max(self.winfo_height(), 2) if self.winfo_height() > 1 else int(self.cget("height"))
        self.delete("all")
        fill = self.hover_fill if self._hover else self.fill
        rounded_rect(self, 1, 1, w - 1, h - 1, self.radius, fill=fill, outline=self.outline or "")
        self.create_text(w / 2, h / 2, text=self.text, fill=self.fg, font=self.font)


class Field(tk.Frame):
    """Labelled input with focus highlight, optional prefix/suffix and placeholder."""

    def __init__(self, parent, label, value="", placeholder="", prefix=None, suffix=None,
                 hint=None, width=10, size=14):
        bg = parent.cget("bg")
        super().__init__(parent, bg=bg)
        if label:
            L(self, label, 12, "bold", C.TEXT).pack(anchor="w", pady=(0, 6))
        self.box = tk.Frame(self, bg=C.SURFACE, highlightthickness=1,
                            highlightbackground=C.BORDER, highlightcolor=C.BORDER)
        self.box.pack(fill="x")
        if prefix:
            tk.Label(self.box, text=prefix, font=F(size, "bold"), fg=C.MUTED,
                     bg=C.SURFACE).pack(side="left", padx=(12, 0))
        self.var = tk.StringVar(value=str(value))
        self.entry = tk.Entry(self.box, textvariable=self.var, font=F(size), relief="flat", bd=0,
                              bg=C.SURFACE, fg=C.INK, insertbackground=C.INK, width=width,
                              highlightthickness=0)
        self.entry.pack(side="left", fill="x", expand=True, padx=(8 if prefix else 12, 12), pady=10)
        if suffix:
            tk.Label(self.box, text=suffix, font=F(size - 1, "bold"), fg=C.MUTED,
                     bg=C.SURFACE).pack(side="right", padx=(0, 12))
        self.hint_text = hint or ""
        self.hint = L(self, self.hint_text, 11, fg=C.MUTED)
        if hint:
            self.hint.pack(anchor="w", pady=(6, 0))
        self.placeholder, self._ph = placeholder, False
        if not str(value) and placeholder:
            self._show_placeholder()
        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

    def _show_placeholder(self):
        self._ph = True
        self.entry.configure(fg=C.SUBTLE)
        self.var.set(self.placeholder)

    def _focus_in(self, _):
        self.box.configure(highlightbackground=C.PRIMARY, highlightcolor=C.PRIMARY)
        if self._ph:
            self._ph = False
            self.var.set("")
            self.entry.configure(fg=C.INK)

    def _focus_out(self, _):
        self.box.configure(highlightbackground=C.BORDER, highlightcolor=C.BORDER)
        if not self.var.get() and self.placeholder:
            self._show_placeholder()

    def get(self):
        return "" if self._ph else self.var.get().strip()

    def clear(self):
        self.var.set("")
        if self.placeholder:
            self._show_placeholder()

    def set_error(self, message=None):
        color = C.DANGER if message else C.BORDER
        self.box.configure(highlightbackground=color, highlightcolor=color)
        text = message or self.hint_text
        self.hint.configure(text=text, fg=C.DANGER if message else C.MUTED)
        if text and not self.hint.winfo_ismapped():
            self.hint.pack(anchor="w", pady=(6, 0))


class Segmented(tk.Frame):
    """Pill-style segmented control (used for categories and filters)."""

    def __init__(self, parent, options, value=None, command=None, colors=None, size=12):
        super().__init__(parent, bg=C.SURFACE_ALT, highlightthickness=1,
                         highlightbackground=C.BORDER, padx=3, pady=3)
        self.options, self.command, self.colors = options, command, colors or {}
        self.value = value or options[0]
        self.buttons = {}
        for opt in options:
            b = tk.Label(self, text=opt, font=F(size, "bold"), padx=14, pady=7, cursor="hand2")
            b.pack(side="left", fill="x", expand=True, padx=1)
            b.bind("<Button-1>", lambda e, o=opt: self.set(o, notify=True))
            self.buttons[opt] = b
        self._paint()

    def set(self, value, notify=False):
        self.value = value
        self._paint()
        if notify and self.command:
            self.command(value)

    def _paint(self):
        for opt, b in self.buttons.items():
            if opt == self.value:
                b.configure(bg=self.colors.get(opt, C.INK), fg="#FFFFFF")
            else:
                b.configure(bg=C.SURFACE_ALT, fg=C.MUTED)


class ProgressBar(tk.Canvas):
    def __init__(self, parent, value=0.0, color=C.PRIMARY, track=C.BORDER, height=10):
        super().__init__(parent, height=height, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        self.value, self.color, self.track, self.h = value, color, track, height
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, value, color=None):
        self.value = value
        self.color = color or self.color
        self._draw()

    def _draw(self):
        w = self.winfo_width()
        if w < 4:
            return
        self.delete("all")
        rounded_rect(self, 0, 0, w, self.h, self.h / 2, fill=self.track)
        v = max(0.0, self.value)
        if v > 0:
            color = C.DANGER if v > 1.0001 else self.color
            rounded_rect(self, 0, 0, max(self.h, w * min(v, 1)), self.h, self.h / 2, fill=color)


class Ring(tk.Canvas):
    """Circular progress indicator with a value in the middle."""

    def __init__(self, parent, value, color, size=150, thickness=14, title="", subtitle=""):
        super().__init__(parent, width=size, height=size, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        p = thickness / 2 + 2
        self.create_oval(p, p, size - p, size - p, outline=C.BORDER, width=thickness)
        v = max(0.0, value)
        if v > 0:
            ring_color = C.DANGER if v > 1.0001 and color != C.GOALS else color
            extent = -359.9 if v >= 1 else -360 * v
            self.create_arc(p, p, size - p, size - p, start=90, extent=extent, style="arc",
                            outline=ring_color, width=thickness)
        self.create_text(size / 2, size / 2 - 9, text=title, font=F(int(size * 0.15), "bold"), fill=C.INK)
        self.create_text(size / 2, size / 2 + 15, text=subtitle, font=F(12), fill=C.MUTED)


class DonutChart(tk.Canvas):
    def __init__(self, parent, data, center_value="", center_label="", height=190):
        super().__init__(parent, height=height, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        self.data, self.cv, self.cl = data, center_value, center_label
        self.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 20:
            return
        self.delete("all")
        r = min(w, h) / 2 - 4
        cx, cy = w / 2, h / 2
        total = sum(v for _, v, _ in self.data)
        box = (cx - r, cy - r, cx + r, cy + r)
        if total <= 0:
            self.create_oval(*box, fill=C.BORDER, outline="")
        else:
            start = 90.0
            for _, v, color in self.data:
                if v <= 0:
                    continue
                extent = max(-359.9, -360 * v / total)
                self.create_arc(*box, start=start, extent=extent, fill=color,
                                outline=self.cget("bg"), width=3, style="pieslice")
                start += extent
        ir = r * 0.64
        self.create_oval(cx - ir, cy - ir, cx + ir, cy + ir, fill=self.cget("bg"), outline="")
        self.create_text(cx, cy - 8, text=self.cv, font=F(20, "bold"), fill=C.INK)
        self.create_text(cx, cy + 16, text=self.cl, font=F(12), fill=C.MUTED)


class BarChart(tk.Canvas):
    """Grouped bar chart. series = [(name, values, color_or_list_of_colors), ...]"""

    def __init__(self, parent, labels, series, height=230, show_values=False):
        super().__init__(parent, height=height, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        self.labels, self.series, self.show_values = labels, series, show_values
        self.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 60:
            return
        self.delete("all")
        ml, mr, mt, mb = 52, 8, 18, 30
        pw, ph = w - ml - mr, h - mt - mb
        top = nice_max(max([max(vals) for _, vals, _ in self.series] + [1]) * 1.08)
        for i in range(5):
            y = mt + ph - ph * i / 4
            self.create_line(ml, y, w - mr, y, fill=C.BORDER)
            self.create_text(ml - 10, y, text=money_short(top * i / 4), anchor="e", font=F(11), fill=C.SUBTLE)
        n, k = len(self.labels), len(self.series)
        gw = pw / n
        bw = min(30, gw * 0.62 / k)
        group = k * bw + (k - 1) * 5
        for i, label in enumerate(self.labels):
            gx = ml + gw * i + gw / 2
            for j, (_, vals, color) in enumerate(self.series):
                v = vals[i]
                col = color[i] if isinstance(color, (list, tuple)) else color
                x0 = gx - group / 2 + j * (bw + 5)
                bh = ph * v / top
                if bh > 0.5:
                    rounded_rect(self, x0, mt + ph - bh, x0 + bw, mt + ph, min(5, bw / 2, bh / 2), fill=col)
                if self.show_values:
                    self.create_text(x0 + bw / 2, mt + ph - bh - 9, text=money_short(v), font=F(10, "bold"), fill=C.MUTED)
            self.create_text(gx, mt + ph + 17, text=label, font=F(11, "bold"), fill=C.MUTED)


class ScrollFrame(tk.Frame):
    """Vertically scrollable area. Put content inside `self.inner`."""

    def __init__(self, parent, bg=C.BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, yscrollincrement=24)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                 style="Finite.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner.bind("<Configure>", lambda e: self._update())
        self.canvas.bind("<Configure>", self._on_canvas)

    def _on_canvas(self, e):
        self.canvas.itemconfigure(self._win, width=e.width)
        self._update()

    def needs_scroll(self):
        return self.inner.winfo_reqheight() > self.canvas.winfo_height() + 1

    def _update(self):
        h = max(self.inner.winfo_reqheight(), self.canvas.winfo_height())
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), h))
        if self.needs_scroll() and not self.vsb.winfo_ismapped():
            self.vsb.pack(side="right", fill="y", before=self.canvas)
        elif not self.needs_scroll() and self.vsb.winfo_ismapped():
            self.vsb.pack_forget()
            self.canvas.yview_moveto(0)

    def scroll(self, units):
        if self.needs_scroll():
            self.canvas.yview_scroll(units, "units")


def setup_styles(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure("Finite.Treeview", background=C.SURFACE, fieldbackground=C.SURFACE,
                foreground=C.TEXT, rowheight=40, font=F(13), borderwidth=0, relief="flat")
    s.configure("Finite.Treeview.Heading", background=C.SURFACE_ALT, foreground=C.MUTED,
                font=F(12, "bold"), relief="flat", borderwidth=0, padding=(10, 9))
    s.map("Finite.Treeview", background=[("selected", C.PRIMARY_SOFT)],
          foreground=[("selected", C.INK)])
    s.map("Finite.Treeview.Heading", background=[("active", C.BORDER)])
    s.layout("Finite.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    for name in ("Finite.Vertical.TScrollbar",):
        s.configure(name, troughcolor=C.BG, background="#CBD5E1", bordercolor=C.BG,
                    lightcolor="#CBD5E1", darkcolor="#CBD5E1", arrowcolor="#CBD5E1",
                    gripcount=0, relief="flat", width=10, arrowsize=10)
        s.map(name, background=[("active", C.SUBTLE)])
        try:
            s.layout(name, [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
                ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
        except tk.TclError:
            pass


def page_header(parent, title, subtitle):
    """Page title on the left; returns the right-hand frame for action buttons."""
    hdr = tk.Frame(parent, bg=C.BG)
    hdr.pack(fill="x", pady=(0, 22))
    left = tk.Frame(hdr, bg=C.BG)
    left.pack(side="left", fill="x", expand=True)
    L(left, title, 26, "bold", C.INK).pack(anchor="w")
    L(left, subtitle, 13, fg=C.MUTED).pack(anchor="w", pady=(4, 0))
    right = tk.Frame(hdr, bg=C.BG)
    right.pack(side="right")
    return right


def card_header(body, title, subtitle=None):
    h = tk.Frame(body, bg=body.cget("bg"))
    h.pack(fill="x", pady=(0, 16))
    left = tk.Frame(h, bg=body.cget("bg"))
    left.pack(side="left", fill="x", expand=True)
    L(left, title, 16, "bold", C.INK).pack(anchor="w")
    if subtitle:
        L(left, subtitle, 12, fg=C.MUTED).pack(anchor="w", pady=(2, 0))
    right = tk.Frame(h, bg=body.cget("bg"))
    right.pack(side="right", anchor="n")
    return right


def grid_row(parent, weights, pady=(0, 20)):
    """A row of columns sized by `weights` (e.g. [2, 1] = two-thirds / one-third)."""
    row = tk.Frame(parent, bg=C.BG)
    row.pack(fill="x", pady=pady)
    for i, w in enumerate(weights):
        row.columnconfigure(i, weight=w, uniform="cols")
    row.rowconfigure(0, weight=1)
    return row


def put(row, widget, col, total, gap=10):
    widget.grid(row=0, column=col, sticky="nsew",
                padx=(0 if col == 0 else gap, 0 if col == total - 1 else gap))


def kv_row(parent, key, value, value_color=None, bold=True):
    r = tk.Frame(parent, bg=parent.cget("bg"))
    r.pack(fill="x", pady=5)
    L(r, key, 13, fg=C.MUTED).pack(side="left")
    L(r, value, 13, "bold" if bold else "normal", fg=value_color or C.INK).pack(side="right")
    return r


def stat_card(parent, label, value, sub, glyph, color, soft, dark=False, progress=None):
    fill = C.SIDEBAR_2 if dark else C.SURFACE
    card = Card(parent, padding=20, fill=fill)
    b = card.body
    icon_badge(b, glyph, color, "#1B3352" if dark else soft, size=36, radius=10).pack(anchor="w")
    L(b, label, 12, "bold", fg=C.SIDEBAR_TEXT if dark else C.MUTED).pack(anchor="w", pady=(14, 0))
    L(b, value, 23, "bold", fg="#FFFFFF" if dark else C.INK).pack(anchor="w", pady=(2, 2))
    wrap_label(b, sub, 12, fg=C.SIDEBAR_TEXT if dark else C.MUTED).pack(fill="x")
    if progress is not None:
        ProgressBar(b, progress, color, track="#223B5C" if dark else C.BORDER, height=6).pack(fill="x", pady=(12, 0))
    return card


def chip(parent, text, color, soft, size=11):
    return tk.Label(parent, text=text, font=F(size, "bold"), fg=color, bg=soft, padx=10, pady=3)


def link(parent, text, command):
    lbl = L(parent, text, 12, "bold", fg=C.PRIMARY, cursor="hand2")
    lbl.bind("<Button-1>", lambda e: command())
    lbl.bind("<Enter>", lambda e: lbl.configure(fg=C.PRIMARY_DARK))
    lbl.bind("<Leave>", lambda e: lbl.configure(fg=C.PRIMARY))
    return lbl


def split_bar(parent, split, height=10):
    """Horizontal stacked bar showing a Needs/Wants/Goals split."""
    c = tk.Canvas(parent, height=height, bg=parent.cget("bg"), highlightthickness=0, bd=0)

    def draw(_=None):
        w = c.winfo_width()
        if w < 10:
            return
        c.delete("all")
        rounded_rect(c, 0, 0, w, height, height / 2, fill=C.BORDER)
        total = sum(split) or 1
        x = 0
        colors = (C.NEEDS, C.WANTS, C.GOALS)
        for i, v in enumerate(split):
            seg = w * v / total
            if seg > 0:
                c.create_rectangle(x + (1 if i else 0), 0, x + seg, height, fill=colors[i], outline="")
            x += seg
        # round the outer ends by masking corners with the background
        bg = c.cget("bg")
        r = height / 2
        for x0, start in ((0, 90), (w - 2 * r, -90)):
            c.create_arc(x0 - 1, -1, x0 + 2 * r + 1, height + 1, start=start, extent=180,
                         style="arc", outline=bg, width=2)

    c.bind("<Configure>", draw)
    c.redraw = draw
    return c


# =============================================================================
# 4. STATE (sample data + simple arithmetic only)
# =============================================================================

class AppState:
    BLUEPRINTS = {
        "standard": ("Standard Balanced Blueprint", (50, 30, 20),
                     "A balanced split for everyday student life."),
        "aggressive": ("Aggressive Savings Blueprint", (40, 20, 40),
                       "Prioritise goals and build savings faster."),
        "custom": ("Custom Framework", None, "Set your own percentages (must total 100%)."),
    }
    CATS = ("Needs", "Wants", "Goals")

    def __init__(self):
        self.name = "Student"
        self.budget = 500.0
        self.rate = 75.0
        self.blueprint = "standard"
        self.pct = {"Needs": 50, "Wants": 30, "Goals": 20}
        today = date.today()
        sample = [("Jeepney fare to campus", 26, "Needs", 7, 45),
                  ("Rice meal and viand", 85, "Needs", 12, 10),
                  ("Photocopy of handouts", 18, "Needs", 13, 5),
                  ("Milk tea", 120, "Wants", 15, 30),
                  ("Savings jar deposit", 50, "Goals", 16, 20)]
        self.transactions = [{"item": i, "amount": float(a), "category": c,
                              "time": datetime.combine(today, time(h, m))}
                             for i, a, c, h, m in sample]

    # --- derived numbers -------------------------------------------------
    def allowance(self, cat):
        return round(self.budget * self.pct[cat] / 100, 2)

    def spent(self, cat):
        return sum(t["amount"] for t in self.transactions if t["category"] == cat)

    @property
    def blueprint_name(self):
        return self.BLUEPRINTS[self.blueprint][0]

    @property
    def split(self):
        return tuple(self.pct[c] for c in self.CATS)

    @property
    def total_expenses(self):
        return self.spent("Needs") + self.spent("Wants")

    @property
    def remaining_spendable(self):
        return self.allowance("Needs") + self.allowance("Wants") - self.total_expenses

    @property
    def saved(self):
        # original: goals_allowance + goals_spent
        return self.allowance("Goals") + self.spent("Goals")

    @property
    def surplus(self):
        # original: unspent_allowance (never below 0)
        return max(0.0, self.remaining_spendable)

    @property
    def projected_savings(self):
        # original: (goals_allowance + goals_spent + unspent_allowance) * 365
        return (self.allowance("Goals") + self.spent("Goals") + self.surplus) * 365

    def hours(self, amount):
        return amount / self.rate if self.rate > 0 else 0

    # --- actions ---------------------------------------------------------
    def add(self, item, amount, category):
        self.transactions.append({"item": item, "amount": amount, "category": category,
                                  "time": datetime.now()})
        over = 0.0
        if category != "Goals":
            over = max(0.0, self.spent(category) - self.allowance(category))
        return over

    def remove(self, index):
        if 0 <= index < len(self.transactions):
            return self.transactions.pop(index)
        return None

    def recommendations(self):
        """Same two actions as the original show_report()."""
        return [f"Transfer {money(self.surplus)} into your Savings Goals right now.",
                f"Move {money(self.surplus)} to an investment/emergency reserve."]


# =============================================================================
# 5. FULL-WINDOW SCREENS: WELCOME + SETUP
# =============================================================================

class WelcomeScreen(tk.Canvas):
    """Branded landing screen, fully drawn on a canvas over a dark gradient."""

    TOP = "#0B1628"

    def __init__(self, parent, app):
        super().__init__(parent, bg=self.TOP, highlightthickness=0, bd=0)
        self.app = app
        self._pending = None
        self.bind("<Configure>", self._schedule)

    def _schedule(self, _=None):
        if self._pending:
            self.after_cancel(self._pending)
        self._pending = self.after(15, self.draw)

    def draw(self):
        self._pending = None
        w, h = self.winfo_width(), self.winfo_height()
        if w < 50:
            return
        self.delete("all")
        self._draw_left(w, h)

    def _draw_left(self, w, h):
        """Minimal centred layout: logo, title, tagline, original intro text, one button."""
        cw = min(640, int(w * 0.6))
        x = (w - cw) / 2
        t = "left"
        draw_logo(self, x, 0, 46, tags=t)
        self.create_text(x + 60, 23, anchor="w", text="FINITE", fill="#FFFFFF", font=F(24, "bold"), tags=t)
        y = 86
        hl = self.create_text(x, y, anchor="nw", width=cw, fill="#FFFFFF", font=F(38, "bold"), tags=t,
                              text="Your Very Own Financial Literacy Coach")
        y = self.bbox(hl)[3] + 12
        tg = self.create_text(x, y, anchor="nw", width=cw, fill="#4FD1A1", font=F(16, "bold"), tags=t,
                              text="Fostering Financial Literacy & Building Financial Awareness")
        y = self.bbox(tg)[3] + 20
        # intro text kept from the original program
        para = ("Financial illiteracy is a prevalent issue in today’s society that FINITE is eager to "
                "address, especially nowadays amid surging inflation. Most people struggle to manage and "
                "allocate their finances, a challenge that can be alleviated through financial literacy. "
                "Developing the habit of saving is a crucial first step toward financial security, as "
                "simply setting aside money increases its value rather than leaving it idle, which is "
                "essential for long-term stability. Its ultimate goal is to lead people toward a financially "
                "literate lifestyle by fostering financial awareness and building good financial habits.")
        pr = self.create_text(x, y, anchor="nw", width=cw, fill=C.SIDEBAR_TEXT, font=F(14), tags=t,
                              text=para)
        y = self.bbox(pr)[3] + 30
        self._button(x, y, "Get Started  →", self.app.show_setup, primary=True)
        x0, y0, x1, y1 = self.bbox(t)
        self.move(t, 0, (h - (y1 - y0)) / 2 - y0)

    def _button(self, x, y, text, command, primary=False):
        font = F(15, "bold")
        bw, bh = measure(font, text) + 52, 52
        tag = f"btn{x}"
        fill, hover = ((C.PRIMARY, C.PRIMARY_DARK) if primary else ("#132A44", "#1B3858"))
        rect = rounded_rect(self, x, y, x + bw, y + bh, 12, fill=fill,
                            outline="" if primary else "#2A4668", tags=(tag, "left"))
        self.create_text(x + bw / 2, y + bh / 2, text=text, fill="#FFFFFF", font=font, tags=(tag, "left"))
        self.tag_bind(tag, "<Enter>", lambda e: (self.itemconfigure(rect, fill=hover), self.configure(cursor="hand2")))
        self.tag_bind(tag, "<Leave>", lambda e: (self.itemconfigure(rect, fill=fill), self.configure(cursor="")))
        self.tag_bind(tag, "<Button-1>", lambda e: command())
        return bw


class BlueprintOption(tk.Frame):
    """Selectable card for one budget blueprint."""

    def __init__(self, parent, key, title, split, desc, on_select):
        super().__init__(parent, bg=C.SURFACE, highlightthickness=2, highlightbackground="#E8ECF2",
                         padx=16, pady=14, cursor="hand2")
        self.key, self.on_select, self.selected = key, on_select, False
        top = tk.Frame(self, bg=C.SURFACE)
        top.pack(fill="x")
        self.radio = tk.Canvas(top, width=20, height=20, bg=C.SURFACE, highlightthickness=0)
        self.radio.pack(side="left")
        L(top, title, 14, "bold", C.INK).pack(side="left", padx=10)
        self.badge = chip(top, " · ".join(f"{v:g}" for v in split) if split else "Your call",
                          C.MUTED, C.SURFACE_ALT)
        self.badge.pack(side="right")
        L(self, desc, 12, fg=C.MUTED).pack(anchor="w", pady=(6, 10), padx=(30, 0))
        self.bar = split_bar(self, split or (34, 33, 33), height=8)
        self.bar.split = split
        self.bar.pack(fill="x", padx=(30, 0))
        self.extra = tk.Frame(self, bg=C.SURFACE)
        for widget in (self, top, self.radio, self.badge, *top.winfo_children(), *self.winfo_children()):
            if not isinstance(widget, tk.Frame) or widget in (self, top):
                widget.bind("<Button-1>", lambda e: self.on_select(self.key))
        self._paint()

    def set_selected(self, value):
        self.selected = value
        self._paint()

    def _paint(self):
        self.configure(highlightbackground=C.PRIMARY if self.selected else "#E8ECF2",
                       highlightcolor=C.PRIMARY if self.selected else "#E8ECF2")
        r = self.radio
        r.delete("all")
        r.create_oval(2, 2, 18, 18, outline=C.PRIMARY if self.selected else "#CBD5E1", width=2)
        if self.selected:
            r.create_oval(6, 6, 14, 14, fill=C.PRIMARY, outline="")


class SetupScreen(ScrollFrame):
    def __init__(self, parent, app, editing=False):
        super().__init__(parent)
        self.app, self.s, self.editing = app, app.state, editing
        self.choice = self.s.blueprint
        wrap = tk.Frame(self.inner, bg=C.BG)
        wrap.pack(fill="both", expand=True, padx=40, pady=(26, 36))

        # top bar
        top = tk.Frame(wrap, bg=C.BG)
        top.pack(fill="x")
        lc = tk.Canvas(top, width=220, height=44, bg=C.BG, highlightthickness=0)
        draw_logo(lc, 0, 2, 40)
        lc.create_text(52, 14, anchor="w", text="FINITE", font=F(20, "bold"), fill=C.INK)
        lc.create_text(52, 33, anchor="w", text="Financial Literacy Coach", font=F(11), fill=C.MUTED)
        lc.pack(side="left")

        # main card (fixed width, centred)
        center = tk.Frame(wrap, bg=C.BG)
        center.pack(pady=(24, 0))
        card = Card(center, padding=36, width=1000)
        card.pack()
        b = card.body
        L(b, "Let's personalise your coach" if not editing else "Update your plan",
          26, "bold", C.INK).pack(anchor="w")
        L(b, "Balancing daily expenses with savings goals is key to building sustainable discipline.",
          13, fg=C.MUTED).pack(anchor="w", pady=(4, 0))
        divider(b, pady=22)

        cols = tk.Frame(b, bg=C.SURFACE)
        cols.pack(fill="x")
        cols.columnconfigure(0, weight=1, uniform="c")
        cols.columnconfigure(1, weight=1, uniform="c")
        left = tk.Frame(cols, bg=C.SURFACE)
        right = tk.Frame(cols, bg=C.SURFACE)
        # original order: Lesson 1 = allocations (left), Lesson 2 = foundation (right)
        right.grid(row=0, column=0, sticky="nsew", padx=(0, 22))
        left.grid(row=0, column=1, sticky="nsew", padx=(22, 0))

        self._lesson(left, "LESSON 2", "Establishing your foundation")
        self.f_name = Field(left, "Your name", value=self.s.name if editing else "",
                            placeholder="e.g. Juan Dela Cruz")
        self.f_name.pack(fill="x", pady=(0, 16))
        self.f_budget = Field(left, "Total daily budget", value=f"{self.s.budget:g}", prefix="₱")
        self.f_budget.pack(fill="x", pady=(0, 16))
        self.f_rate = Field(left, "Hourly earnings or allowance rate", value=f"{self.s.rate:g}", prefix="₱",
                            suffix="/ hour", hint="Shows the opportunity cost of each purchase. Enter 0 to skip.")
        self.f_rate.pack(fill="x", pady=(0, 18))

        # live plan preview
        pv = tk.Frame(left, bg=C.SURFACE_ALT, highlightthickness=1, highlightbackground=C.BORDER,
                      padx=16, pady=14)
        pv.pack(fill="x")
        L(pv, "YOUR DAILY PLAN PREVIEW", 11, "bold", C.MUTED).pack(anchor="w")
        self.preview_bar = split_bar(pv, self.s.split, height=10)
        self.preview_bar.pack(fill="x", pady=(10, 10))
        self.preview_rows = {}
        for cat in AppState.CATS:
            r = tk.Frame(pv, bg=C.SURFACE_ALT)
            r.pack(fill="x", pady=2)
            tk.Frame(r, bg=CATEGORY[cat]["color"], width=10, height=10).pack(side="left")
            name = L(r, cat, 12, fg=C.TEXT)
            name.pack(side="left", padx=8)
            val = L(r, "", 12, "bold", C.INK)
            val.pack(side="right")
            self.preview_rows[cat] = (name, val)

        self._lesson(right, "LESSON 1", "Balancing budget allocations")
        self.options = {}
        for key, (title, split, desc) in AppState.BLUEPRINTS.items():
            opt = BlueprintOption(right, key, title, split, desc, self.select)
            opt.pack(fill="x", pady=(0, 12))
            self.options[key] = opt
        # custom percentage inputs live inside the Custom card
        ext = self.options["custom"].extra
        row = tk.Frame(ext, bg=C.SURFACE)
        row.pack(fill="x", pady=(12, 0))
        self.f_custom = {}
        for i, cat in enumerate(AppState.CATS):
            f = Field(row, cat, value=f"{self.s.pct[cat]:g}", suffix="%", width=4, size=13)
            f.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0))
            row.columnconfigure(i, weight=1, uniform="p")
            self.f_custom[cat] = f
        self.total_lbl = L(ext, "", 12, "bold")
        self.total_lbl.pack(anchor="w", pady=(8, 0))

        self.error = L(b, "", 13, "bold", C.DANGER)
        self.error.pack(anchor="w", pady=(18, 0))
        divider(b, pady=(10, 20))
        foot = tk.Frame(b, bg=C.SURFACE)
        foot.pack(fill="x")
        L(foot, "You can change these anytime from the sidebar.", 12, fg=C.MUTED).pack(side="left")
        RoundedButton(foot, "Save & Open Dashboard  →" if editing else "Start Coaching  →",
                      self.submit, height=46, size=14).pack(side="right")
        RoundedButton(foot, "Cancel" if editing else "Back", self.cancel, kind="ghost",
                      height=46, size=14).pack(side="right", padx=12)

        for f in (self.f_budget, *self.f_custom.values()):
            f.var.trace_add("write", lambda *a: self.refresh_preview())
        self.select(self.choice)

    def _lesson(self, parent, tag, title):
        r = tk.Frame(parent, bg=C.SURFACE)
        r.pack(fill="x", pady=(0, 16))
        chip(r, tag, C.PRIMARY_DARK, C.PRIMARY_SOFT).pack(side="left")
        L(r, title, 16, "bold", C.INK).pack(side="left", padx=10)

    def select(self, key):
        self.choice = key
        for k, opt in self.options.items():
            opt.set_selected(k == key)
        extra = self.options["custom"].extra
        if key == "custom":
            extra.pack(fill="x", padx=(30, 0))
        else:
            extra.pack_forget()
        self.refresh_preview()

    def current_split(self):
        if self.choice != "custom":
            return AppState.BLUEPRINTS[self.choice][1]
        vals = []
        for cat in AppState.CATS:
            try:
                vals.append(float(self.f_custom[cat].get() or 0))
            except ValueError:
                vals.append(0.0)
        return tuple(vals)

    def refresh_preview(self):
        split = self.current_split()
        try:
            budget = max(0.0, float(self.f_budget.get() or 0))
        except ValueError:
            budget = 0.0
        for cat, pct in zip(AppState.CATS, split):
            name, val = self.preview_rows[cat]
            name.configure(text=f"{cat}  ({pct:g}%)")
            val.configure(text=money(budget * pct / 100))
        self.preview_bar.split = split
        self.preview_bar.redraw_with = split
        self._redraw_split(self.preview_bar, split)
        self._redraw_split(self.options["custom"].bar, split if self.choice == "custom" else (34, 33, 33))
        total = sum(split)
        ok = abs(total - 100) < 0.1
        self.total_lbl.configure(text=f"Total: {total:g}%" + ("  ✓ Ready" if ok else "  (must equal 100%)"),
                                 fg=C.PRIMARY_DARK if ok else C.DANGER)

    @staticmethod
    def _redraw_split(bar, split):
        """Swap the values a split_bar draws and repaint it."""
        w, h = bar.winfo_width(), int(bar.cget("height"))
        if w < 10:
            bar.after(50, lambda: SetupScreen._redraw_split(bar, split))
            return
        bar.delete("all")
        rounded_rect(bar, 0, 0, w, h, h / 2, fill=C.BORDER)
        total = sum(split) or 1
        x = 0
        for i, v in enumerate(split):
            seg = w * max(0, v) / total
            if seg > 0:
                rounded_rect(bar, x, 0, x + seg, h, h / 2, fill=(C.NEEDS, C.WANTS, C.GOALS)[i])
            x += seg

    def submit(self):
        self.error.configure(text="")
        for f in (self.f_budget, self.f_rate, *self.f_custom.values()):
            f.set_error(None)
        try:
            budget = float(self.f_budget.get())
            if budget <= 0:
                raise ValueError
        except ValueError:
            self.f_budget.set_error("Please enter an amount greater than 0.")
            return
        try:
            rate = float(self.f_rate.get() or 0)
            if rate < 0:
                raise ValueError
        except ValueError:
            self.f_rate.set_error("Please enter numbers only (or 0 to skip).")
            return
        split = self.current_split()
        if self.choice == "custom" and abs(sum(split) - 100) >= 0.1:
            self.error.configure(text="Your custom percentages must add up to exactly 100%.")
            return
        s = self.s
        s.name = self.f_name.get() or "Student"
        s.budget, s.rate, s.blueprint = budget, rate, self.choice
        s.pct = dict(zip(AppState.CATS, split))
        self.app.show_shell("dashboard")
        self.app.toast(f"Plan saved. Welcome aboard, {s.name}! Your protected savings target is "
                       f"{money(s.allowance('Goals'))}.")

    def cancel(self):
        if self.editing:
            self.app.show_shell("dashboard")
        else:
            self.app.show_welcome()


# =============================================================================
# 6. SHELL (sidebar + content) AND PAGES
# =============================================================================

class NavItem(tk.Frame):
    def __init__(self, parent, glyph, text, command):
        super().__init__(parent, bg=C.SIDEBAR, cursor="hand2")
        self.active, self.hover = False, False
        self.bar = tk.Frame(self, width=4, bg=C.SIDEBAR)
        self.bar.pack(side="left", fill="y")
        self.inner = tk.Frame(self, bg=C.SIDEBAR, padx=14, pady=11)
        self.inner.pack(side="left", fill="both", expand=True, padx=(10, 14))
        self.icon = tk.Canvas(self.inner, width=22, height=22, bg=C.SIDEBAR, highlightthickness=0)
        self.icon.pack(side="left")
        self.glyph = glyph
        self.label = tk.Label(self.inner, text=text, font=F(14, "bold"), bg=C.SIDEBAR, fg=C.SIDEBAR_TEXT)
        self.label.pack(side="left", padx=12)
        for w in (self, self.inner, self.icon, self.label):
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", lambda e: self._hover(True))
            w.bind("<Leave>", lambda e: self._hover(False))
        self._paint()

    def _hover(self, value):
        self.hover = value
        self._paint()

    def set_active(self, value):
        self.active = value
        self._paint()

    def _paint(self):
        bg = C.SIDEBAR_HOVER if (self.active or self.hover) else C.SIDEBAR
        fg = "#FFFFFF" if self.active else ("#DCE5F2" if self.hover else C.SIDEBAR_TEXT)
        self.bar.configure(bg=C.PRIMARY if self.active else C.SIDEBAR)
        for w in (self.inner, self.icon, self.label):
            w.configure(bg=bg)
        self.label.configure(fg=fg)
        self.icon.delete("all")
        draw_glyph(self.icon, self.glyph, 11, 11, "#5EE0B0" if self.active else fg)


class Sidebar(tk.Frame):
    MAIN = (("dashboard", "dashboard", "Dashboard"),
            ("budget", "budget", "Budget Allocation"),
            ("expenses", "expenses", "Expense Tracker"),
            ("report", "report", "Literacy Report"))

    def __init__(self, parent, app):
        super().__init__(parent, bg=C.SIDEBAR, width=260)
        self.pack_propagate(False)
        self.app, self.items = app, {}
        logo = tk.Canvas(self, height=92, bg=C.SIDEBAR, highlightthickness=0)
        logo.pack(fill="x")
        draw_logo(logo, 26, 26, 40)
        logo.create_text(78, 38, anchor="w", text="FINITE", fill="#FFFFFF", font=F(20, "bold"))
        logo.create_text(78, 58, anchor="w", text="Financial Literacy Coach", fill=C.SIDEBAR_TEXT, font=F(11))
        tk.Frame(self, bg="#1A2B44", height=1).pack(fill="x", padx=22)
        self._section("MENU")
        for key, glyph, text in self.MAIN:
            item = NavItem(self, glyph, text, lambda k=key: app.navigate(k))
            item.pack(fill="x", pady=1)
            self.items[key] = item

        # profile block (bottom)
        s = app.state
        prof = tk.Frame(self, bg=C.SIDEBAR_2, padx=14, pady=12)
        prof.pack(side="bottom", fill="x", padx=16, pady=18)
        av = tk.Canvas(prof, width=40, height=40, bg=C.SIDEBAR_2, highlightthickness=0)
        av.create_oval(0, 0, 40, 40, fill=C.PRIMARY, outline="")
        av.create_text(20, 20, text=(s.name[:1] or "S").upper(), fill="#FFFFFF", font=F(16, "bold"))
        av.pack(side="left")
        info = tk.Frame(prof, bg=C.SIDEBAR_2)
        info.pack(side="left", padx=12, fill="x", expand=True)
        tk.Label(info, text=s.name[:20], font=F(13, "bold"), fg="#FFFFFF", bg=C.SIDEBAR_2,
                 anchor="w").pack(fill="x")
        tk.Label(info, text=s.blueprint_name.replace(" Blueprint", ""), font=F(11),
                 fg=C.SIDEBAR_TEXT, bg=C.SIDEBAR_2, anchor="w").pack(fill="x")

        exit_item = NavItem(self, "exit", "Back to Welcome", app.show_welcome)
        exit_item.pack(side="bottom", fill="x", pady=1)
        setup_item = NavItem(self, "setup", "Edit Setup", lambda: app.show_setup(editing=True))
        setup_item.pack(side="bottom", fill="x", pady=1)
        tk.Label(self, text="ACCOUNT", font=F(11, "bold"), fg="#52657F", bg=C.SIDEBAR,
                 anchor="w").pack(side="bottom", fill="x", padx=28, pady=(0, 6))

    def _section(self, text):
        tk.Label(self, text=text, font=F(11, "bold"), fg="#52657F", bg=C.SIDEBAR,
                 anchor="w").pack(fill="x", padx=28, pady=(22, 8))

    def set_active(self, key):
        for k, item in self.items.items():
            item.set_active(k == key)


class Page(ScrollFrame):
    """Base class for pages inside the shell. Subclasses implement build()."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app, self.s = app, app.state
        self.body = tk.Frame(self.inner, bg=C.BG)
        self.body.pack(fill="both", expand=True, padx=36, pady=(30, 34))
        self.build()

    def build(self):
        raise NotImplementedError


class DashboardPage(Page):
    def build(self):
        s, b = self.s, self.body
        right = page_header(b, f"{greeting()}, {s.name}",
                            f"{date.today():%A, %B %d, %Y}  ·  Here's your financial snapshot for today.")
        RoundedButton(right, "+  Add Expense", lambda: self.app.navigate("expenses")).pack(side="right")
        RoundedButton(right, "View Report", lambda: self.app.navigate("report"), kind="ghost").pack(side="right", padx=10)

        spendable = s.allowance("Needs") + s.allowance("Wants")
        row = grid_row(b, [1, 1, 1, 1])
        cards = [
            stat_card(row, "Total Daily Budget", money(s.budget), s.blueprint_name,
                      "wallet", C.INK, C.SURFACE_ALT),
            stat_card(row, "Remaining Spendable", money(s.remaining_spendable),
                      f"of {money(spendable)} for needs & wants", "trend", C.NEEDS, C.NEEDS_SOFT,
                      progress=max(0, s.remaining_spendable) / spendable if spendable else 0),
            stat_card(row, "Total Expenses", money(s.total_expenses),
                      f"{sum(1 for t in s.transactions if t['category'] != 'Goals')} purchases logged today",
                      "receipt", C.WANTS, C.WANTS_SOFT),
            stat_card(row, "Savings Allocation", money(s.allowance("Goals")),
                      f"Protected target  ·  {money(s.saved)} saved", "shield", C.GOALS, C.GOALS_SOFT),
        ]
        for i, c in enumerate(cards):
            put(row, c, i, 4)

        row = grid_row(b, [3, 2])
        put(row, self._overview(row), 0, 2)
        put(row, self._breakdown(row), 1, 2)

        self._recent(b).pack(fill="x")

    def _overview(self, parent):
        s = self.s
        card = Card(parent)
        right = card_header(card.body, "Budget Overview", f"{s.blueprint_name}  ·  "
                            + " / ".join(f"{p:g}" for p in s.split) + " split")
        link(right, "Details  →", lambda: self.app.navigate("budget")).pack()
        split_bar(card.body, s.split, height=12).pack(fill="x", pady=(0, 20))
        for cat in AppState.CATS:
            color = CATEGORY[cat]["color"]
            a = s.allowance(cat)
            r = tk.Frame(card.body, bg=C.SURFACE)
            r.pack(fill="x", pady=(0, 16))
            top = tk.Frame(r, bg=C.SURFACE)
            top.pack(fill="x")
            tk.Frame(top, bg=color, width=10, height=10).pack(side="left")
            L(top, f"{cat}", 13, "bold", C.INK).pack(side="left", padx=8)
            L(top, f"{s.pct[cat]:g}%", 12, fg=C.MUTED).pack(side="left")
            if cat == "Goals":
                val, ratio = f"{money(s.saved)} saved  ·  target {money(a)}", 1.0
                note = "Protected - do not spend"
            else:
                sp = s.spent(cat)
                val, ratio = f"{money(sp)} of {money(a)}", sp / a if a else 0
                note = (f"{money(a - sp)} remaining" if sp <= a else f"Over by {money(sp - a)}")
            L(top, val, 13, "bold", C.INK).pack(side="right")
            ProgressBar(r, ratio, color, height=8).pack(fill="x", pady=(8, 4))
            bot = tk.Frame(r, bg=C.SURFACE)
            bot.pack(fill="x")
            L(bot, note, 11, fg=C.DANGER if ratio > 1 and cat != "Goals" else C.MUTED).pack(side="left")
            L(bot, f"{ratio * 100:.0f}%", 11, "bold", C.MUTED).pack(side="right")
        return card

    def _breakdown(self, parent):
        s = self.s
        card = Card(parent)
        card_header(card.body, "Spending Breakdown", "Where today's budget went")
        data = [("Needs", s.spent("Needs"), C.NEEDS), ("Wants", s.spent("Wants"), C.WANTS),
                ("Saved", s.saved, C.GOALS), ("Unspent", s.surplus, "#D5DCE6")]
        DonutChart(card.body, data, money_short(s.total_expenses), "spent today", height=180).pack(fill="x")
        legend = tk.Frame(card.body, bg=C.SURFACE)
        legend.pack(fill="x", pady=(16, 0))
        total = sum(v for _, v, _ in data) or 1
        for name, v, color in data:
            r = tk.Frame(legend, bg=C.SURFACE)
            r.pack(fill="x", pady=4)
            dot = tk.Canvas(r, width=10, height=10, bg=C.SURFACE, highlightthickness=0)
            dot.create_oval(0, 0, 10, 10, fill=color, outline="")
            dot.pack(side="left")
            L(r, name, 13, fg=C.TEXT).pack(side="left", padx=10)
            L(r, f"{v / total * 100:.0f}%", 12, fg=C.MUTED, width=5, anchor="e").pack(side="right")
            L(r, money(v), 13, "bold", C.INK).pack(side="right")
        return card

    def _recent(self, parent):
        s = self.s
        card = Card(parent)
        right = card_header(card.body, "Recent Transactions", "Your latest activity today")
        link(right, "View all  →", lambda: self.app.navigate("expenses")).pack()
        recent = list(reversed(s.transactions))[:5]
        if not recent:
            L(card.body, "No transactions yet. Log your first expense to get started.", 13,
              fg=C.MUTED).pack(anchor="w", pady=20)
        for i, t in enumerate(recent):
            transaction_row(card.body, t, s)
            if i < len(recent) - 1:
                divider(card.body, pady=2, color="#EEF2F6")
        return card



def transaction_row(parent, t, s):
    cat = t["category"]
    meta = CATEGORY[cat]
    r = tk.Frame(parent, bg=parent.cget("bg"))
    r.pack(fill="x", pady=8)
    av = tk.Canvas(r, width=38, height=38, bg=parent.cget("bg"), highlightthickness=0)
    av.create_oval(0, 0, 38, 38, fill=meta["soft"], outline="")
    av.create_text(19, 19, text=cat[0], fill=meta["color"], font=F(14, "bold"))
    av.pack(side="left")
    mid = tk.Frame(r, bg=parent.cget("bg"))
    mid.pack(side="left", padx=14, fill="x", expand=True)
    L(mid, t["item"], 13, "bold", C.INK).pack(anchor="w")
    L(mid, f"{cat}  ·  {t['time']:%I:%M %p}".replace(" 0", " "), 11, fg=C.MUTED).pack(anchor="w")
    if cat == "Goals":
        L(r, f"+{money(t['amount'])}", 13, "bold", C.GOALS).pack(side="right")
    else:
        L(r, f"−{money(t['amount'])}", 13, "bold", C.INK).pack(side="right")


class BudgetPage(Page):
    def build(self):
        s, b = self.s, self.body
        right = page_header(b, "Budget Allocation",
                            f"{s.blueprint_name}  ·  {money(s.budget)} daily budget split into needs, wants and goals.")
        RoundedButton(right, "Change Blueprint", lambda: self.app.show_setup(editing=True), kind="ghost").pack(side="right")

        row = grid_row(b, [1, 1, 1])
        for i, cat in enumerate(AppState.CATS):
            put(row, self._category_card(row, cat), i, 3)

    def _category_card(self, parent, cat):
        s = self.s
        meta = CATEGORY[cat]
        a = s.allowance(cat)
        card = Card(parent, padding=24)
        b = card.body
        top = tk.Frame(b, bg=C.SURFACE)
        top.pack(fill="x")
        chip(top, cat.upper() if cat != "Goals" else "GOALS / SAVINGS", meta["color"], meta["soft"]).pack(side="left")
        L(top, f"{s.pct[cat]:g}%", 26, "bold", C.INK).pack(side="right")
        wrap_label(b, meta["desc"], 12, fg=C.MUTED).pack(fill="x", pady=(10, 14))
        if cat == "Goals":
            ratio = 1.0  # original: the goals allowance is protected automatically
            ring = Ring(b, ratio, meta["color"], title="Secured", subtitle="do not spend")
        else:
            sp = s.spent(cat)
            ratio = sp / a if a else 0
            ring = Ring(b, ratio, meta["color"], title=money_short(a - sp) if sp <= a else "Over",
                        subtitle="remaining" if sp <= a else f"by {money_short(sp - a)}")
        ring.pack(pady=(4, 16))
        if cat == "Goals":
            kv_row(b, "Allocated percentage", f"{s.pct[cat]:g}%")
            kv_row(b, "Protected savings target", money(a))
            kv_row(b, "Extra savings deposits", money(s.spent("Goals")))
            kv_row(b, "Amount saved", money(s.saved), C.GOALS)
        else:
            sp = s.spent(cat)
            kv_row(b, "Allocated percentage", f"{s.pct[cat]:g}%")
            kv_row(b, "Total allowance", money(a))
            kv_row(b, "Amount spent", money(sp))
            kv_row(b, "Remaining balance", money(a - sp), C.DANGER if sp > a else C.PRIMARY_DARK)
        pb = tk.Frame(b, bg=C.SURFACE)
        pb.pack(fill="x", pady=(14, 0))
        ProgressBar(pb, ratio, meta["color"], height=10).pack(fill="x")
        cap = tk.Frame(b, bg=C.SURFACE)
        cap.pack(fill="x", pady=(6, 0))
        L(cap, "Saved" if cat == "Goals" else "Used", 11, fg=C.MUTED).pack(side="left")
        L(cap, f"{ratio * 100:.0f}%", 11, "bold", C.MUTED).pack(side="right")
        return card


class ExpensesPage(Page):
    def build(self):
        s, b = self.s, self.body
        page_header(b, "Expense Tracker",
                    f"Log spending and build mindfulness  \u00b7  Safe spendable left today: {money(s.remaining_spendable)}")

        row = grid_row(b, [2, 3])
        put(row, self._form(row), 0, 2)
        put(row, self._history(row), 1, 2)

    def _form(self, parent):
        s = self.s
        card = Card(parent, padding=26)
        b = card.body
        card_header(b, "Log an Expense / Saving")
        self.f_item = Field(b, "Item description", placeholder="e.g. Lunch at the canteen")
        self.f_item.pack(fill="x", pady=(0, 16))
        self.f_amount = Field(b, "Expense amount", placeholder="0.00", prefix="₱")
        self.f_amount.pack(fill="x", pady=(0, 16))
        L(b, "Category", 12, "bold", C.TEXT).pack(anchor="w", pady=(0, 6))
        self.seg = Segmented(b, ["Needs", "Wants", "Goals"], "Needs", command=lambda v: self._update_preview(),
                             colors={c: CATEGORY[c]["color"] for c in CATEGORY})
        self.seg.pack(fill="x")
        self.cat_hint = L(b, "", 11, fg=C.MUTED)
        self.cat_hint.pack(anchor="w", pady=(6, 14))

        self.oc = tk.Frame(b, bg=C.GOLD_SOFT, padx=14, pady=10)
        L(self.oc, "OPPORTUNITY COST", 11, "bold", "#8A5A12").pack(anchor="w")
        self.oc_text = wrap_label(self.oc, "", 12, fg="#6B4710")
        self.oc_text.pack(fill="x")

        self.msg = L(b, "", 12, "bold", C.DANGER)
        self.msg.pack(anchor="w", pady=(10, 0))
        btns = tk.Frame(b, bg=C.SURFACE)
        btns.pack(fill="x", pady=(8, 0))
        btns.columnconfigure(0, weight=2)
        btns.columnconfigure(1, weight=1)
        RoundedButton(btns, "+  Add Expense", self.add, height=46, size=14).grid(row=0, column=0, sticky="ew")
        RoundedButton(btns, "Clear", self.clear, kind="ghost", height=46, size=14).grid(
            row=0, column=1, sticky="ew", padx=(10, 0))
        self.f_amount.var.trace_add("write", lambda *a: self._update_preview())
        self.f_amount.entry.bind("<Return>", lambda e: self.add())
        self.f_item.entry.bind("<Return>", lambda e: self.f_amount.entry.focus_set())
        self._update_preview()
        return card

    def _update_preview(self):
        s, cat = self.s, self.seg.value
        labels = {"Needs": "Need (Essential)", "Wants": "Want (Lifestyle/Leisure)",
                  "Goals": "Extra Savings Deposit"}
        self.cat_hint.configure(text=labels[cat])
        try:
            amount = float(self.f_amount.get() or 0)
        except ValueError:
            amount = 0
        # original rule: only shown when hourly rate > 0 and category is not Goals
        if s.rate > 0 and cat != "Goals" and amount > 0:
            self.oc_text.configure(text=f"This purchase is equivalent to working "
                                        f"{s.hours(amount):.1f} hours of your life!")
            if not self.oc.winfo_ismapped():
                self.oc.pack(fill="x", before=self.msg)
        else:
            self.oc.pack_forget()

    def _history(self, parent):
        s = self.s
        card = Card(parent, padding=24)
        b = card.body
        right = card_header(b, "Transaction History", f"{len(s.transactions)} entries today")
        self.filter = Segmented(right, ["All", "Needs", "Wants", "Goals"], "All",
                                command=lambda v: self._fill(), size=11)
        self.filter.pack()
        wrap = tk.Frame(b, bg=C.SURFACE, highlightthickness=1, highlightbackground=C.BORDER)
        wrap.pack(fill="both", expand=True)
        cols = ("no", "time", "item", "cat", "amount")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings", style="Finite.Treeview",
                                 height=9, selectmode="browse")
        for col, text, width, anchor, stretch in (("no", "#", 40, "center", False),
                                                  ("time", "Time", 88, "w", False),
                                                  ("item", "Description", 140, "w", True),
                                                  ("cat", "Category", 100, "w", False),
                                                  ("amount", "Amount", 104, "e", False)):
            self.tree.heading(col, text=text, anchor=anchor)
            self.tree.column(col, width=width, minwidth=60 if stretch else width,
                             anchor=anchor, stretch=stretch)
        self.tree.tag_configure("odd", background="#FAFBFD")
        self.tree.tag_configure("Goals", foreground=C.PRIMARY_DARK)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview, style="Finite.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        foot = tk.Frame(b, bg=C.SURFACE)
        foot.pack(fill="x", pady=(14, 0))
        RoundedButton(foot, "Delete Selected", self.delete, kind="danger", height=38, size=12).pack(side="left")
        self.total_lbl = L(foot, "", 13, "bold", C.INK)
        self.total_lbl.pack(side="right")
        self._fill()
        return card

    def _fill(self):
        self.tree.delete(*self.tree.get_children())
        flt = self.filter.value
        total, n = 0.0, 0
        for idx, t in enumerate(self.s.transactions):
            if flt != "All" and t["category"] != flt:
                continue
            sign = "+" if t["category"] == "Goals" else "−"
            tags = (("odd",) if n % 2 else ()) + ((t["category"],) if t["category"] == "Goals" else ())
            self.tree.insert("", "end", iid=str(idx), tags=tags, values=(
                idx + 1, t["time"].strftime("%I:%M %p").lstrip("0"), t["item"],
                "● " + t["category"], f"{sign}{money(t['amount'])}"))
            total += t["amount"]
            n += 1
        label = "Total" if flt == "All" else f"{flt} total"
        self.total_lbl.configure(text=f"{label}:  {money(total)}")

    def clear(self):
        self.f_item.clear()
        self.f_amount.clear()
        self.f_amount.set_error(None)
        self.msg.configure(text="")
        self.focus_set()

    def add(self):
        self.f_amount.set_error(None)
        try:
            amount = float(self.f_amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.f_amount.set_error("Please enter an amount greater than zero.")
            return
        item = self.f_item.get() or "Unspecified item"
        cat = self.seg.value
        over = self.s.add(item, amount, cat)
        msg = f"Logged {item} ({money(amount)}) under {cat}."
        if over > 0:
            self.app.toast(f"BUDGET LIMIT EXCEEDED: {self.s.name}, you are overspent on {cat} "
                           f"by {money(over)}.", "danger")
        else:
            self.app.toast(msg)
        self.app.navigate("expenses", animate=False)

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            self.app.toast("Select a transaction in the table first.", "info")
            return
        t = self.s.remove(int(sel[0]))
        if t:
            self.app.toast(f"Removed {t['item']} ({money(t['amount'])}).", "info")
        self.app.navigate("expenses", animate=False)


class ReportPage(Page):
    """End-of-day report - same content and logic as the original show_report()."""

    def build(self):
        s, b = self.s, self.body
        right = page_header(b, f"{s.name.upper()}'S END-OF-DAY LITERACY & EFFICIENCY REPORT",
                            f"Report Date: {date.today():%B %d, %Y}")
        RoundedButton(right, "Export Report", lambda: self.app.toast(
            "Export is a demonstration action in this prototype.", "info"), kind="ghost").pack(side="right")

        row = grid_row(b, [1, 1, 1])
        cards = [
            stat_card(row, "Total Spent", money(s.total_expenses),
                      f"of {money(s.allowance('Needs') + s.allowance('Wants'))} spendable", "receipt",
                      C.WANTS, C.WANTS_SOFT),
            stat_card(row, "Unused Surplus", money(s.surplus), "Excess spendable funds", "wallet",
                      C.NEEDS, C.NEEDS_SOFT),
            stat_card(row, "Saved Goals", money(s.saved), "Protected target + extra deposits",
                      "shield", C.GOALS, C.GOALS_SOFT),
        ]
        for i, c in enumerate(cards):
            put(row, c, i, 3)

        row = grid_row(b, [2, 3])
        put(row, self._summary(row), 0, 2)
        put(row, self._comparison(row), 1, 2)

        row = grid_row(b, [2, 3])
        put(row, self._savings(row), 0, 2)
        put(row, self._framework(row), 1, 2)

        self._projection(b)

    def _summary(self, parent):
        s = self.s
        card = Card(parent)
        card_header(card.body, "Logged Expenditures Today")
        items = s.transactions
        if not items:
            L(card.body, "No expenditures logged today! Excellent job, keep it up!", 13,
              fg=C.PRIMARY_DARK).pack(anchor="w", pady=10)
        for i, t in enumerate(items[:6]):
            r = tk.Frame(card.body, bg=C.SURFACE)
            r.pack(fill="x", pady=4)
            L(r, f"{i + 1}.", 12, fg=C.SUBTLE, width=3).pack(side="left")
            meta = CATEGORY[t["category"]]
            chip(r, t["category"], meta["color"], meta["soft"], size=10).pack(side="left", padx=(0, 10))
            L(r, t["item"][:26], 13, fg=C.TEXT).pack(side="left")
            L(r, money(t["amount"]), 13, "bold", C.INK).pack(side="right")
        if len(items) > 6:
            L(card.body, f"+ {len(items) - 6} more in the Expense Tracker", 12, fg=C.MUTED).pack(anchor="w", pady=(4, 0))
        divider(card.body, pady=12)
        L(card.body, f"Financial Allocations & Tracking Summary, {s.name}", 12, "bold",
          C.MUTED).pack(anchor="w", pady=(0, 4))
        kv_row(card.body, "Needs Spent", f"{money(s.spent('Needs'))} / {money(s.allowance('Needs'))}")
        kv_row(card.body, "Wants Spent", f"{money(s.spent('Wants'))} / {money(s.allowance('Wants'))}")
        kv_row(card.body, "Saved Goals", money(s.saved), C.GOALS)
        return card

    def _comparison(self, parent):
        s = self.s
        card = Card(parent)
        right = card_header(card.body, "Budget Allocation Comparison", "Allowance vs. actual")
        for name, color in (("Allowance", "#D5DCE6"), ("Actual", C.INK)):
            tk.Frame(right, bg=color, width=10, height=10).pack(side="left", padx=(12, 6))
            L(right, name, 12, fg=C.MUTED).pack(side="left")
        BarChart(card.body, ["Needs", "Wants", "Goals"],
                 [("Allowance", [s.allowance(c) for c in AppState.CATS], "#D5DCE6"),
                  ("Actual", [s.spent("Needs"), s.spent("Wants"), s.saved], [C.NEEDS, C.WANTS, C.GOALS])],
                 height=280, show_values=True).pack(fill="x")
        return card

    def _savings(self, parent):
        s = self.s
        card = Card(parent)
        card_header(card.body, "Savings Progress")
        inner = tk.Frame(card.body, bg=C.SURFACE)
        inner.pack(fill="x")
        Ring(inner, 1.0, C.GOALS, size=150, thickness=14, title=money_short(s.saved),
             subtitle="saved").pack(side="left")
        info = tk.Frame(inner, bg=C.SURFACE)
        info.pack(side="left", fill="both", expand=True, padx=(22, 0))
        kv_row(info, "Protected target", money(s.allowance("Goals")))
        kv_row(info, "Extra deposits", money(s.spent("Goals")))
        kv_row(info, "Saved Goals", money(s.saved), C.GOALS)
        kv_row(info, "Unused surplus", money(s.surplus), C.WANTS if s.surplus > 0 else C.MUTED)
        return card

    def _framework(self, parent):
        s = self.s
        card = Card(parent)
        card_header(card.body, "FINITE Decision Framework", "No Unused Funds Rule")
        if s.surplus <= 0:
            banner = tk.Frame(card.body, bg=C.PRIMARY_SOFT, padx=16, pady=12)
            banner.pack(fill="x")
            wrap_label(banner, f"SAVINGS GOALS ACHIEVED: Excellent budget allocation, {s.name}! "
                       "There is no idle spendable funds remaining!", 13, "#0A6B4A", "bold").pack(fill="x")
            return card
        banner = tk.Frame(card.body, bg=C.GOLD_SOFT, padx=16, pady=12)
        banner.pack(fill="x", pady=(0, 14))
        L(banner, f"UNUSED SURPLUS FOUND: You have {money(s.surplus)} in excess spendable funds.", 13,
          "bold", "#8A5A12").pack(anchor="w")
        wrap_label(banner, "According to FINITE objectives, leaving extra funds uninvested can slow down your "
                   "savings growth! Instead of keeping the same amount at the end of each year, allow your "
                   "earnings to accumulate so they grow over time and your rewards become more significant "
                   "each time!", 12, fg="#6B4710").pack(fill="x", pady=(4, 0))
        L(card.body, "COMPOUNDING GROWTH", 11, "bold", C.MUTED).pack(anchor="w")
        wrap_label(card.body, "Compounding growth: the process where an asset's earnings, from either capital "
                   "gains or interest, are reinvested to generate their own earnings over time, causing your "
                   "money to grow exponentially rather than linearly. In short, it is earning interest on "
                   "your interest.", 13, fg=C.TEXT).pack(fill="x", pady=(4, 14))
        L(card.body, "RECOMMENDED ACTIONS", 11, "bold", C.MUTED).pack(anchor="w", pady=(0, 4))
        for i, text in enumerate(s.recommendations()):
            r = tk.Frame(card.body, bg=C.SURFACE)
            r.pack(fill="x", pady=4)
            num = tk.Canvas(r, width=24, height=24, bg=C.SURFACE, highlightthickness=0)
            num.create_oval(0, 0, 24, 24, fill=C.INK, outline="")
            num.create_text(12, 12, text=str(i + 1), fill="#FFFFFF", font=F(11, "bold"))
            num.pack(side="left")
            L(r, text, 13, fg=C.TEXT).pack(side="left", padx=12)
        return card

    def _projection(self, parent):
        s = self.s
        card = Card(parent, padding=26)
        card.pack(fill="x")
        b = card.body
        card_header(b, "Future Habits Projection")
        L(b, money(s.projected_savings), 34, "bold", C.PRIMARY_DARK).pack(anchor="w")
        wrap_label(b, "If you maintain this daily saving discipline, you will amass approximately this amount "
                   "in 1 year! (It could be more if you invest further!)", 13, fg=C.MUTED).pack(fill="x", pady=(6, 0))


class Shell(tk.Frame):
    PAGES = {"dashboard": DashboardPage, "budget": BudgetPage,
             "expenses": ExpensesPage, "report": ReportPage}

    def __init__(self, parent, app):
        super().__init__(parent, bg=C.BG)
        self.app = app
        self.sidebar = Sidebar(self, app)
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self, bg=C.BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.page = None
        self.key = None

    def show(self, key, animate=True):
        self.key = key
        self.sidebar.set_active(key)
        old, new = self.page, self.PAGES[key](self.content, self.app)
        self.page = new
        self.app.current_scroll = new
        new.place(x=0, y=0, relwidth=1, relheight=1)
        if old is not None:
            old.destroy()
        if animate:
            self.app.slide_in(new)


# =============================================================================
# 7. APP
# =============================================================================

class FiniteApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FINITE — Your Very Own Financial Literacy Coach")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(1360, sw - 60), min(860, sh - 80)
        self.root.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 3)}")
        self.root.minsize(1180, 720)
        self.root.configure(bg=C.BG)
        self._set_icon()
        Fonts.init(self.root)
        setup_styles(self.root)
        self.state = AppState()
        self.screen = None
        self.shell = None
        self.current_scroll = None
        self._toast = None
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.root.bind_all(seq, self._on_wheel)
        self.show_welcome()

    def _set_icon(self):
        img = tk.PhotoImage(width=32, height=32)
        img.put(C.PRIMARY, to=(0, 0, 32, 32))
        for i, top in enumerate((20, 14, 8)):
            img.put("#FFFFFF", to=(7 + i * 7, top, 11 + i * 7, 26))
        img.put(C.GOLD, to=(24, 4, 28, 8))
        self.root.iconphoto(True, img)
        self._icon = img

    # --- navigation --------------------------------------------------------
    def _swap(self, new):
        old, self.screen = self.screen, new
        new.place(x=0, y=0, relwidth=1, relheight=1)
        if old is not None:
            old.destroy()
        self.slide_in(new)

    def show_welcome(self):
        self.shell = None
        self.current_scroll = None
        self._swap(WelcomeScreen(self.root, self))

    def show_setup(self, editing=False):
        self.shell = None
        screen = SetupScreen(self.root, self, editing=editing)
        self.current_scroll = screen
        self._swap(screen)

    def show_shell(self, key="dashboard"):
        self.shell = Shell(self.root, self)
        self._swap(self.shell)
        self.shell.show(key, animate=False)

    def navigate(self, key, animate=True):
        if self.shell is None:
            self.show_shell(key)
        elif self.shell.key != key or not animate:
            self.shell.show(key, animate=animate)

    def slide_in(self, widget, offsets=(34, 22, 13, 7, 3, 1, 0)):
        """Small slide-from-right page transition."""
        def step(i=0):
            if not widget.winfo_exists():
                return
            widget.place_configure(x=offsets[i])
            if i + 1 < len(offsets):
                widget.after(14, step, i + 1)
        step()

    # --- feedback ----------------------------------------------------------
    def toast(self, message, kind="success"):
        color = {"success": C.PRIMARY, "danger": C.DANGER, "info": C.NEEDS, "warning": C.GOLD}[kind]
        if self._toast is not None and self._toast.winfo_exists():
            self._toast.destroy()
        t = tk.Frame(self.root, bg=C.INK)
        tk.Frame(t, bg=color, width=5).pack(side="left", fill="y")
        tk.Label(t, text=message, font=F(13), fg="#F1F5F9", bg=C.INK, padx=16, pady=13,
                 wraplength=380, justify="left").pack(side="left")
        close = tk.Label(t, text="✕", font=F(12, "bold"), fg="#94A3B8", bg=C.INK, padx=12, cursor="hand2")
        close.pack(side="right", fill="y")
        close.bind("<Button-1>", lambda e: t.destroy())
        t.place(relx=1, rely=1, x=-28, y=-28, anchor="se")
        t.lift()
        self._toast = t
        t.after(3800, lambda: t.winfo_exists() and t.destroy())

    def _on_wheel(self, e):
        sf = self.current_scroll
        if sf is None or not sf.winfo_exists() or isinstance(e.widget, (ttk.Treeview, str)):
            return
        if e.num == 4:
            units = -2
        elif e.num == 5:
            units = 2
        else:
            units = -2 if e.delta > 0 else 2
        sf.scroll(units)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FiniteApp().run()
