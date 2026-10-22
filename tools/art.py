"""Inline SVG artwork shared by build.py and tools/make_brand.py: perspective tennis court, tennis ball, lesson-area diagram.
Everything is drawn from geometry (no photos)."""

NAVY, COURT, COURT_OUT, OPTIC, WHITE = '#0a1128', '#1d43a6', '#142f7a', '#d7f205', '#ffffff'

# perspective camera (court units = feet; u across, v along from the near baseline)
_K, _D, _C, _H, _CX = 467.0, 40.0, 24806.0, -100.0, 240.0


def P(u, v, h=0.0):
    z = v + _D
    return (_CX + u * _K / z, _H + _C / z - h * _K / z)


def _line(a, b, cls='ln'):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return f'<path class="{cls}" pathLength="1" d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}"/>'


def _poly(pts):
    return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in (P(*p) for p in pts)) + 'Z'


def ball(cx, cy, r, fill=OPTIC, seam=NAVY, sw=None):
    k = r / 46.0
    sw = sw or 5.5 * k
    X = lambda v: cx + (v - 50) * k
    Y = lambda v: cy + (v - 50) * k
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>'
            f'<g fill="none" stroke="{seam}" stroke-width="{sw:.2f}" stroke-linecap="round" opacity=".85">'
            f'<path d="M{X(17):.1f} {Y(20):.1f}C{X(40):.1f} {Y(36):.1f} {X(40):.1f} {Y(64):.1f} {X(17):.1f} {Y(80):.1f}"/>'
            f'<path d="M{X(83):.1f} {Y(20):.1f}C{X(60):.1f} {Y(36):.1f} {X(60):.1f} {Y(64):.1f} {X(83):.1f} {Y(80):.1f}"/></g>')


def court_svg(cls='court', title=None, ball_on=True):
    """Portrait perspective court, viewBox 0 0 480 600."""
    out = _poly([(-30, -14), (30, -14), (30, 92), (-30, 92)])
    surf = _poly([(-18, 0), (18, 0), (18, 78), (-18, 78)])
    L = []
    for u in (-18, -13.5, 13.5, 18):
        L.append(_line((u, 0), (u, 78)))
    for v in (0, 78):
        L.append(_line((-18, v), (18, v)))
    for v in (18, 60):
        L.append(_line((-13.5, v), (13.5, v)))
    L.append(_line((0, 18), (0, 60)))
    L.append(_line((0, 0), (0, 0.9)))
    L.append(_line((0, 78), (0, 77.1)))
    # net
    nl, nr = P(-21, 39), P(21, 39)
    tl, tr, tc = P(-21, 39, 3.5), P(21, 39, 3.5), P(0, 39, 3.0)
    mesh = ''.join(_line((u, 39, 0), (u, 39, 3.2), 'mesh') for u in range(-20, 21, 2))
    net = (f'<path class="netfill" d="M{nl[0]:.1f} {nl[1]:.1f}L{nr[0]:.1f} {nr[1]:.1f}L{tr[0]:.1f} {tr[1]:.1f}'
           f'Q{tc[0]:.1f} {tc[1]+1.5:.1f} {tl[0]:.1f} {tl[1]:.1f}Z"/>{mesh}'
           f'<path class="tape" pathLength="1" d="M{tl[0]:.1f} {tl[1]:.1f}Q{tc[0]:.1f} {tc[1]+1.5:.1f} {tr[0]:.1f} {tr[1]:.1f}"/>'
           f'<path class="post" d="M{tl[0]:.1f} {tl[1]:.1f}L{nl[0]:.1f} {nl[1]:.1f}M{tr[0]:.1f} {tr[1]:.1f}L{nr[0]:.1f} {nr[1]:.1f}"/>')
    art = ''
    if ball_on:
        # flight: from in front of the near baseline, over the net, landing deep in the far service box
        a, b = (8.0, 6.0, 3.5), (-6.0, 54.0, 0.0)
        pts = []
        for i in range(41):
            t = i / 40
            u = a[0] + (b[0] - a[0]) * t
            v = a[1] + (b[1] - a[1]) * t
            h = a[2] * (1 - t) + 7.0 * 4 * t * (1 - t)
            pts.append(P(u, v, h))
        arc = 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        land = P(*b)
        sx, sy = P(b[0], b[1])
        art = (f'<path class="arc" d="{arc}"/>'
               f'<ellipse class="bounce" cx="{land[0]:.1f}" cy="{land[1]:.1f}" rx="9" ry="3"/>'
               f'<g class="ball">{ball(pts[0][0], pts[0][1], 26)}</g>')
    t = f'<title>{title}</title>' if title else ''
    role = 'role="img" aria-label="' + title + '"' if title else 'aria-hidden="true" focusable="false"'
    return (f'<svg class="{cls}" viewBox="0 0 480 600" {role} preserveAspectRatio="xMidYMid slice">{t}'
            f'<defs><linearGradient id="cg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16388f"/>'
            f'<stop offset="1" stop-color="{COURT}"/></linearGradient>'
            f'<radialGradient id="glow" cx=".5" cy=".95" r=".7"><stop offset="0" stop-color="#ffffff" stop-opacity=".10"/>'
            f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="480" height="600" fill="{COURT_OUT}"/><path d="{out}" fill="{COURT_OUT}"/>'
            f'<path d="{surf}" fill="url(#cg)"/><rect width="480" height="600" fill="url(#glow)"/>'
            f'<g class="lines">{"".join(L)}</g><g class="net">{net}</g>{art}</svg>')


# lesson area: towns from towns.json (lon/lat) fitted into a 480x340 box. Stylised diagram, not a map.
def _fit(towns, w=480, h=340, px=70, py=46):
    import math
    k = math.cos(math.radians(41.45))
    xs = [t['lon'] * k for t in towns]; ys = [t['lat'] for t in towns]
    s = min((w - 2 * px) / (max(xs) - min(xs)), (h - 2 * py) / (max(ys) - min(ys)))
    ox = (w - s * (max(xs) - min(xs))) / 2; oy = (h - s * (max(ys) - min(ys))) / 2
    return lambda lon, lat: (ox + (lon * k - min(xs)) * s, h - oy - (lat - min(ys)) * s)


def area_svg(towns, hub='Middlebury'):
    if all(t.get('map') for t in towns):
        pts = {t['name']: tuple(t['map']) for t in towns}
    else:
        xy = _fit(towns, h=360)
        pts = {t['name']: xy(t['lon'], t['lat']) for t in towns}
    hx, hy = pts[hub]
    rings = ''.join(f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="{r}" class="ring"/>' for r in (70, 140, 210, 280))
    spokes = ''.join(f'<path class="link" pathLength="1" d="M{hx:.0f} {hy:.0f}L{x:.0f} {y:.0f}"/>'
                     for n, (x, y) in pts.items() if n != hub)
    dots = ''
    for t in towns:
        x, y = pts[t['name']]
        lab = t.get('label', 'start')
        if lab == 'middle-below':
            a, tx, ty = 'middle', x, y + (36 if t['name'] == hub else 32)
        elif lab == 'middle-above':
            a, tx, ty = 'middle', x, y - 22
        elif lab == 'end':
            a, tx, ty = 'end', x - 16, y + 5
        else:
            a, tx, ty = 'start', x + 16, y + 5
        big = ' hubdot' if t['name'] == hub else ''
        dots += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{9 if big else 7}" class="dot{big}"/>'
                 f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{18 if big else 14}" class="halo"/>'
                 f'<text x="{tx:.0f}" y="{ty:.0f}" text-anchor="{a}">{t["name"]}</text>')
    return (f'<svg class="area-art" viewBox="0 0 480 360" aria-hidden="true" focusable="false">'
            f'<g class="grid">{rings}<path d="M0 {hy:.0f}H480M{hx:.0f} 0V360" class="axis"/></g>{spokes}{dots}</svg>')
