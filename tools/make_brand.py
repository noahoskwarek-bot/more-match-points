#!/usr/bin/env python3
"""Make the tennis-ball mark, favicons, app icons and the 1200x630 share image (images/og-image.png).

No photos: everything is drawn from SVG/HTML and rendered with headless Chrome, then the .ico is made with Pillow.
    python3 tools/make_brand.py      # needs google-chrome (or chromium) and Pillow
Re-run after changing colours, the price or the header text, then commit the files it writes.
"""
import json, os, shutil, subprocess, tempfile, html
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GREEN, DEEP, BALL, WHITE = '#1b5e20', '#0f3d17', '#c8f03c', '#ffffff'
site = json.load(open(os.path.join(ROOT, 'site.json'), encoding='utf-8'))


def ball(cx=50, cy=50, r=46, seam=WHITE, outline=None):
    """A tennis ball: yellow-green circle with two curved white seams, in a 100x100 box by default."""
    k = r / 46
    def X(v): return cx + (v - 50) * k
    def Y(v): return cy + (v - 50) * k
    o = f' stroke="{outline}" stroke-width="{3*k:.2f}"' if outline else ''
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BALL}"{o}/>'
            f'<g fill="none" stroke="{seam}" stroke-width="{6*k:.2f}" stroke-linecap="round">'
            f'<path d="M{X(17):.2f} {Y(20):.2f}C{X(40):.2f} {Y(36):.2f} {X(40):.2f} {Y(64):.2f} {X(17):.2f} {Y(80):.2f}"/>'
            f'<path d="M{X(83):.2f} {Y(20):.2f}C{X(60):.2f} {Y(36):.2f} {X(60):.2f} {Y(64):.2f} {X(83):.2f} {Y(80):.2f}"/></g>')


MARK = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{ball(outline=GREEN)}</svg>\n'
FAVICON = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="{GREEN}"/>'
           f'{ball(50, 50, 36)}</svg>\n')


def og_html():
    e = html.escape
    areas = ' · '.join(site['areas']) + ', ' + site['state']
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{background:{GREEN};color:{WHITE};font-family:Oswald,"Inter",sans-serif;position:relative}}
.band{{position:absolute;left:0;right:0;top:0;height:14px;background:{BALL}}}
.wrap{{position:absolute;left:80px;top:56px;width:720px}}
.top{{font-size:40px;letter-spacing:3px;text-transform:uppercase;color:{BALL};font-weight:600}}
h1{{font-size:100px;line-height:1;margin:12px 0 22px;text-transform:uppercase;font-weight:700}}
.price{{display:inline-block;background:{WHITE};color:{GREEN};font-size:48px;font-weight:700;padding:10px 28px;border-radius:12px;border-left:14px solid {BALL}}}
.meta{{font-family:Montserrat,"Inter",sans-serif;font-size:27px;line-height:1.35;margin-top:24px;font-weight:600}}
.phone{{font-size:38px;color:{BALL};margin-top:10px;font-weight:600}}
svg{{position:absolute;right:70px;top:150px;width:340px;height:340px}}
</style></head><body><div class="band"></div><div class="wrap">
<div class="top">{e(site["brand_sub"])}</div>
<h1>{e(site["name"])}</h1>
<div class="price">${site["price"]} / {e(site["lesson_length"].upper())}</div>
<div class="meta">Private tennis lessons with {e(site["coach"])}<br>{e(areas)}</div>
<div class="phone">Request a lesson online</div></div>
<svg viewBox="0 0 100 100">{ball(seam=GREEN)}</svg></body></html>'''


def chrome():
    for c in ('google-chrome', 'chromium', 'chromium-browser'):
        if shutil.which(c):
            return c
    raise SystemExit('needs google-chrome or chromium')


def shot(markup, out, w, h):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'p.html')
        open(src, 'w', encoding='utf-8').write(markup)
        subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                        '--force-device-scale-factor=1', f'--window-size={w},{h}', f'--screenshot={out}',
                        '--default-background-color=00000000', 'file://' + src],
                       check=True, capture_output=True)
    im = Image.open(out).convert('RGBA').crop((0, 0, w, h))
    im.save(out, optimize=True)


def svg_page(svg, size):
    return f'<!doctype html><html><body style="margin:0;background:transparent"><div style="width:{size}px;height:{size}px">{svg.replace("<svg ", f"<svg width=\"{size}\" height=\"{size}\" ")}</div></body></html>'


def main():
    os.makedirs(os.path.join(ROOT, 'brand'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'images'), exist_ok=True)
    open(os.path.join(ROOT, 'brand', 'mark.svg'), 'w').write(MARK)
    open(os.path.join(ROOT, 'favicon.svg'), 'w').write(FAVICON)
    # app icons: full-bleed square (iOS rounds the corners itself)
    full = FAVICON.replace(' rx="22"', '')
    for name, size, svg in (('apple-touch-icon.png', 180, full), ('icon-192.png', 192, full), ('icon-512.png', 512, full),
                            ('brand/mark-512.png', 512, MARK)):
        shot(svg_page(svg, size), os.path.join(ROOT, name), size, size)
    ico_src = os.path.join(ROOT, 'brand', '_fav.png')
    shot(svg_page(FAVICON, 256), ico_src, 256, 256)
    Image.open(ico_src).save(os.path.join(ROOT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    os.remove(ico_src)
    og = os.path.join(ROOT, 'images', 'og-image.png')
    shot(og_html(), og, 1200, 630)
    Image.open(og).convert('RGB').save(og, optimize=True)
    print('wrote brand/mark.svg, brand/mark-512.png, favicon.svg, favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png, images/og-image.png')


if __name__ == '__main__':
    main()
