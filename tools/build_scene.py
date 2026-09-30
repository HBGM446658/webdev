"""Generate the layered Santorini hero illustration used on the BellMitchell site.

Every layer shares one 1600x900 viewBox so the layers line up when stacked,
and each one can be moved independently for scroll parallax.

    python3 tools/build_scene.py   # writes assets/scene-*.svg
"""
import random
from pathlib import Path

W, H = 1600, 900
HORIZON = 575
OUT = Path(__file__).resolve().parent.parent / "assets"

BLUE = "#1d5fa8"
BLUE_DARK = "#154a86"
WHITE = "#fdfaf3"
SHADE = "#eadfcb"


def svg(body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMax slice">'
        f"<defs>{defs}</defs>{body}</svg>\n"
    )


def write(name, content):
    (OUT / f"scene-{name}.svg").write_text(content)


# --------------------------------------------------------------------------
# Sky, far islands and sea
# --------------------------------------------------------------------------
def back():
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#7fb8df"/>
      <stop offset=".45" stop-color="#b9d6e6"/>
      <stop offset=".78" stop-color="#f6d8b4"/>
      <stop offset="1" stop-color="#fde6c3"/>
    </linearGradient>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5d9fca"/>
      <stop offset=".35" stop-color="#2f78b0"/>
      <stop offset="1" stop-color="#0f3f6e"/>
    </linearGradient>
    <radialGradient id="glint" cx=".5" cy="0" r=".6">
      <stop offset="0" stop-color="#ffe9b8" stop-opacity=".85"/>
      <stop offset="1" stop-color="#ffe9b8" stop-opacity="0"/>
    </radialGradient>
    <filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
    <style>
      .ripple{animation:drift 9s ease-in-out infinite alternate}
      .ripple:nth-child(2n){animation-duration:12s;animation-direction:alternate-reverse}
      @keyframes drift{from{transform:translateX(-18px)}to{transform:translateX(18px)}}
      @media (prefers-reduced-motion:reduce){.ripple{animation:none}}
    </style>"""
    parts = [f'<rect width="{W}" height="{HORIZON + 2}" fill="url(#sky)"/>']
    # hazy clouds
    for cx, cy, rx, ry, o in [(260, 150, 240, 26, .55), (1320, 110, 300, 30, .5),
                              (980, 250, 200, 18, .4), (520, 300, 180, 14, .35)]:
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" opacity="{o}" filter="url(#soft)"/>')
    # distant islands on the horizon
    parts.append(
        f'<path d="M560 {HORIZON} C620 548 700 540 760 552 C800 546 850 556 900 {HORIZON} Z" fill="#9fb3c8" opacity=".75"/>'
        f'<path d="M1040 {HORIZON} C1090 556 1160 548 1230 560 C1270 556 1300 566 1330 {HORIZON} Z" fill="#aabdce" opacity=".7"/>'
    )
    parts.append(f'<rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#sea)"/>')
    parts.append(f'<rect y="{HORIZON - 2}" width="{W}" height="5" fill="#fff4dc" opacity=".55"/>')
    # sun path on the water
    parts.append(f'<clipPath id="seaOnly"><rect y="{HORIZON}" width="{W}" height="{H - HORIZON}"/></clipPath>'
                 f'<ellipse cx="800" cy="{HORIZON}" rx="260" ry="330" fill="url(#glint)" clip-path="url(#seaOnly)"/>')
    rnd = random.Random(7)
    ripples = []
    for i in range(70):
        y = HORIZON + 8 + (i / 70) ** 1.6 * (H - HORIZON - 10)
        spread = 60 + (y - HORIZON) * 0.9
        x = 800 + rnd.uniform(-spread, spread)
        w = 8 + (y - HORIZON) * rnd.uniform(.08, .22)
        o = max(.12, .75 - (y - HORIZON) / 420) * rnd.uniform(.5, 1)
        ripples.append(f'<rect class="ripple" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{1.5 + (y - HORIZON) / 140:.1f}" rx="2" fill="#fff3d6" opacity="{o:.2f}"/>')
    for i in range(40):
        y = HORIZON + 20 + rnd.random() ** 1.3 * (H - HORIZON - 20)
        x = rnd.uniform(0, W)
        w = 20 + (y - HORIZON) * rnd.uniform(.1, .3)
        ripples.append(f'<rect class="ripple" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="2" rx="1" fill="#cfe6f5" opacity=".22"/>')
    parts.append("<g>" + "".join(ripples) + "</g>")
    write("back", svg("".join(parts), defs))


def sun():
    defs = """
    <radialGradient id="halo"><stop offset="0" stop-color="#ffd98a" stop-opacity=".85"/>
      <stop offset=".3" stop-color="#ffcf7a" stop-opacity=".3"/><stop offset=".65" stop-color="#ffcf7a" stop-opacity=".08"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/></radialGradient>
    <clipPath id="skyOnly"><rect width="1600" height="575"/></clipPath>
    <linearGradient id="disc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff0c2"/><stop offset="1" stop-color="#ffc35c"/></linearGradient>"""
    body = ('<g clip-path="url(#skyOnly)"><g class="sun">'
            '<circle cx="800" cy="500" r="340" fill="url(#halo)"/>'
            '<circle cx="800" cy="500" r="68" fill="url(#disc)"/></g></g>')
    write("sun", svg(body, defs))


# --------------------------------------------------------------------------
# Buildings
# --------------------------------------------------------------------------
def house(x, y, w, h, rnd, colour=WHITE):
    """A cubic Cycladic house with its base at (x, y)."""
    top = y - h
    out = [f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{colour}"/>',
           f'<rect x="{x + w * .72:.1f}" y="{top}" width="{w * .28:.1f}" height="{h}" fill="{SHADE}" opacity=".7"/>',
           f'<rect x="{x - 2}" y="{top - 3}" width="{w + 4}" height="4" fill="{colour}"/>']
    if rnd.random() < .35:  # barrel-vault roof
        out.append(f'<path d="M{x} {top} Q{x + w / 2} {top - w * .35} {x + w} {top} Z" fill="{colour}"/>')
    # door + windows
    kind = rnd.choice([BLUE, BLUE, "#2a7fb8", "#c9553a"])
    if h > 22:
        dw = max(5, w * .18)
        out.append(f'<rect x="{x + w * .2:.1f}" y="{y - h * .5:.1f}" width="{dw:.1f}" height="{h * .5:.1f}" rx="{dw / 2:.1f}" fill="{kind}"/>')
    if w > 26:
        out.append(f'<rect x="{x + w * .55:.1f}" y="{top + h * .25:.1f}" width="{w * .13:.1f}" height="{h * .22:.1f}" fill="{kind}"/>')
    return "".join(out)


def dome(cx, base, r, cross=True):
    out = [f'<rect x="{cx - r * 1.05:.1f}" y="{base - r * .5:.1f}" width="{r * 2.1:.1f}" height="{r * .5:.1f}" fill="{WHITE}"/>',
           f'<path d="M{cx - r} {base - r * .5:.1f} A{r} {r} 0 0 1 {cx + r} {base - r * .5:.1f} Z" fill="{BLUE}"/>',
           f'<path d="M{cx + r * .25:.1f} {base - r * 1.45:.1f} A{r} {r} 0 0 1 {cx + r} {base - r * .5:.1f} L{cx + r * .25:.1f} {base - r * .5:.1f} Z" fill="{BLUE_DARK}" opacity=".6"/>']
    if cross:
        t = base - r * 1.5
        out.append(f'<rect x="{cx - 1.2:.1f}" y="{t - 12:.1f}" width="2.4" height="13" fill="{WHITE}"/>'
                   f'<rect x="{cx - 5:.1f}" y="{t - 9:.1f}" width="10" height="2.4" fill="{WHITE}"/>')
    return "".join(out)


def bell_tower(cx, base, h):
    """The small arched belfry — a quiet nod to the Bell in BellMitchell."""
    w = h * .55
    x = cx - w / 2
    return (f'<path d="M{x} {base} V{base - h * .75:.1f} Q{cx} {base - h * 1.05:.1f} {x + w:.1f} {base - h * .75:.1f} V{base} Z" fill="{WHITE}"/>'
            f'<path d="M{x + w * .22:.1f} {base - h * .3:.1f} V{base - h * .62:.1f} Q{cx} {base - h * .82:.1f} {x + w * .78:.1f} {base - h * .62:.1f} V{base - h * .3:.1f} Z" fill="#1b3a57"/>'
            f'<path d="M{cx - 6:.1f} {base - h * .38:.1f} Q{cx - 6:.1f} {base - h * .56:.1f} {cx} {base - h * .56:.1f} Q{cx + 6:.1f} {base - h * .56:.1f} {cx + 6:.1f} {base - h * .38:.1f} Z" fill="#e2a83c"/>'
            f'<rect x="{cx - 1.2:.1f}" y="{base - h * 1.2:.1f}" width="2.4" height="{h * .2:.1f}" fill="{WHITE}"/>'
            f'<rect x="{cx - 5:.1f}" y="{base - h * 1.14:.1f}" width="10" height="2.4" fill="{WHITE}"/>')


def cliff_defs():
    return """
    <linearGradient id="rock" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#c98459"/><stop offset=".5" stop-color="#a45f3d"/><stop offset="1" stop-color="#6e3a26"/>
    </linearGradient>
    <linearGradient id="rockSide" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#3b1d12" stop-opacity=".35"/>
    </linearGradient>"""


def village():
    rnd = random.Random(21)
    # Cliff: high on the left, falling to the sea around x=640
    edge = [(0, 380), (90, 372), (200, 392), (300, 420), (390, 452), (470, 498), (540, 548), (600, 600), (650, 660), (690, 760), (700, 900)]
    d = "M0 900 V380 " + " ".join(f"L{x} {y}" for x, y in edge[1:]) + " L0 900 Z"
    parts = [f'<clipPath id="cliff"><path d="{d}"/></clipPath>',
             f'<path d="{d}" fill="url(#rock)"/>', f'<path d="{d}" fill="url(#rockSide)"/>', '<g clip-path="url(#cliff)">']
    for i in range(9):
        y = 470 + i * 45
        parts.append(f'<path d="M0 {y} Q{200 + i * 15} {y - 18} {420 + i * 30} {y + 6}" stroke="#7d432b" stroke-width="3" fill="none" opacity=".35"/>')
    parts.append('</g>')

    def ridge(x):
        for (x0, y0), (x1, y1) in zip(edge, edge[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return edge[-1][1]

    # Terraced rows of houses stepping down the cliff face
    buildings = []
    for row in range(5):
        x = -10 + row * 14
        limit = 560 - row * 70
        while x < limit:
            w = rnd.randint(30, 58)
            h = rnd.randint(24, 44)
            base = ridge(x + w / 2) + 6 + row * 46
            colour = WHITE if rnd.random() > .12 else rnd.choice(["#f3c98b", "#f1b8a0"])
            buildings.append((base, house(x, base, w, h, rnd, colour)))
            x += w + rnd.randint(-4, 6)
    buildings.sort(key=lambda b: b[0])
    parts += [b[1] for b in buildings]
    # Blue domes on top
    parts.append(dome(150, ridge(150) - 30, 26))
    parts.append(house(118, ridge(150) - 2, 64, 30, rnd))
    parts.append(dome(420, ridge(420) + 30, 18))
    parts.append(dome(300, ridge(300) + 60, 14, cross=False))
    write("village", svg("".join(parts), cliff_defs()))


def chapel():
    rnd = random.Random(5)
    d = ("M1600 900 V470 L1540 468 L1470 486 L1400 512 L1330 548 L1270 590 "
         "L1220 640 L1190 700 L1175 900 Z")
    parts = [f'<clipPath id="cliff"><path d="{d}"/></clipPath>', f'<path d="{d}" fill="url(#rock)"/>', '<g clip-path="url(#cliff)">']
    for i in range(6):
        y = 560 + i * 55
        parts.append(f'<path d="M1600 {y} Q{1420 - i * 10} {y - 14} {1150 - i * 12} {y + 10}" stroke="#7d432b" stroke-width="3" fill="none" opacity=".35"/>')
    parts.append('</g>')
    parts.append(house(1300, 560, 50, 30, rnd))
    parts.append(house(1520, 480, 70, 40, rnd))
    # chapel body, dome and bell tower
    parts.append(f'<rect x="1380" y="444" width="120" height="72" fill="{WHITE}"/>'
                 f'<rect x="1470" y="444" width="30" height="72" fill="{SHADE}" opacity=".7"/>'
                 f'<path d="M1418 516 V486 Q1430 472 1442 486 V516 Z" fill="{BLUE}"/>')
    parts.append(dome(1440, 446, 34))
    parts.append(bell_tower(1395, 446, 64))
    parts.append(f'<rect x="1370" y="512" width="150" height="6" fill="{WHITE}"/>')
    write("chapel", svg("".join(parts), cliff_defs()))


def boat():
    body = f"""
    <g id="b">
      <path d="M760 668 L884 668 Q876 690 850 694 L790 694 Q770 690 760 668 Z" fill="{WHITE}"/>
      <path d="M760 668 L884 668 L882 674 L762 674 Z" fill="{BLUE}"/>
      <rect x="818" y="540" width="3" height="128" fill="#3a3a3a"/>
      <path d="M822 546 L822 660 L882 660 Z" fill="#fff8ea"/>
      <path d="M816 556 L816 660 L772 660 Z" fill="#f4e6cf"/>
      <path d="M822 546 L846 552 L822 560 Z" fill="#d9653b"/>
    </g>
    <g opacity=".28" transform="translate(0 1366) scale(1 -1)"><use href="#b"/></g>"""
    write("boat", svg(body))


def flowers():
    rnd = random.Random(11)
    pinks = ["#d6247a", "#e0408c", "#c21a6b", "#ef5fa2", "#b3165c"]
    greens = ["#3f6b2a", "#4f7d33", "#2f5520"]
    parts = []
    # Branches hanging from the top-right corner
    parts.append('<path d="M1600 0 C1540 60 1500 120 1470 200 M1600 40 C1560 120 1530 170 1540 260 M1560 0 C1500 40 1430 70 1380 60" '
                 'stroke="#5a3a24" stroke-width="7" fill="none" stroke-linecap="round"/>')

    def cluster(cx, cy, n, spread):
        for _ in range(n):
            x, y = cx + rnd.gauss(0, spread), cy + rnd.gauss(0, spread * .8)
            if rnd.random() < .35:
                parts.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.randint(8, 14)}" ry="{rnd.randint(4, 7)}" '
                             f'transform="rotate({rnd.randint(0, 180)} {x:.0f} {y:.0f})" fill="{rnd.choice(greens)}"/>')
            else:
                r = rnd.randint(6, 12)
                parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{rnd.choice(pinks)}"/>'
                             f'<circle cx="{x - r * .3:.0f}" cy="{y - r * .3:.0f}" r="{r * .35:.1f}" fill="#fff" opacity=".25"/>')

    for cx, cy, n, s in [(1560, 40, 90, 50), (1480, 150, 70, 40), (1540, 250, 60, 36),
                         (1400, 60, 55, 34), (1600, 150, 60, 40)]:
        cluster(cx, cy, n, s)
    # Bottom-left foreground bush
    for cx, cy, n, s in [(40, 870, 90, 60), (150, 900, 70, 50), (-10, 780, 50, 40)]:
        cluster(cx, cy, n, s)
    write("flowers", svg("".join(parts)))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    back(); sun(); village(); chapel(); boat(); flowers()
    print("wrote", sorted(p.name for p in OUT.glob("scene-*.svg")))
