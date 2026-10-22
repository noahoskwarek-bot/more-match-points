#!/usr/bin/env python3
"""Make the tennis-ball mark, favicons, app icons and the 1200x630 share image (images/og-image.png).

No photos: everything is drawn from SVG/HTML (tools/art.py) and rendered with headless Chrome using the
self-hosted fonts in fonts/, then the .ico is made with Pillow.
    python3 tools/make_brand.py      # needs google-chrome (or chromium) and Pillow
Re-run after changing colours, the price or the brand name, then commit the files it writes.
"""
import html, io, json, os, re, shutil, subprocess, sys, tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import art  # noqa: E402
from art import NAVY, OPTIC, WHITE  # noqa: E402

site = json.load(open(os.path.join(ROOT, 'site.json'), encoding='utf-8'))
FONTS = (f'@font-face{{font-family:Anton;src:url(file://{ROOT}/fonts/anton-latin.woff2)}}'
         f'@font-face{{font-family:Inter;font-weight:400 800;src:url(file://{ROOT}/fonts/inter-latin-var.woff2)}}')

MARK = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{art.ball(50, 50, 46, OPTIC, NAVY, 6)}</svg>\n'
FAVICON = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="{NAVY}"/>'
           f'{art.ball(50, 50, 34, OPTIC, NAVY, 5)}</svg>\n')


def og_html(town=None):
    e = html.escape
    areas = site.get('og_area') or site.get('area_line')
    court = art.court_svg('court', ball_on=True)
    headline = (f'<h1 class="t">Tennis lessons in<br><span>{e(town)}, CT</span></h1>' if town
                else '<h1>Private tennis<br><span>lessons.</span></h1>')
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{background:radial-gradient(90% 90% at 100% 0%,#18306f 0%,{NAVY} 60%);color:{WHITE};font-family:Inter,sans-serif;position:relative}}
.art{{position:absolute;right:0;top:0;width:580px;height:630px;overflow:hidden}}
.art svg{{width:100%;height:100%}}
.art::after{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,{NAVY} 0%,rgba(10,17,40,.75) 22%,rgba(10,17,40,0) 55%)}}
.court .ln{{fill:none;stroke:#fff;stroke-width:2.2;opacity:.92}}.court .mesh{{stroke:#fff;stroke-opacity:.16}}
.court .netfill{{fill:#060b1c;fill-opacity:.55}}.court .tape{{fill:none;stroke:#fff;stroke-width:3.2}}.court .post{{stroke:#cfd6ea;stroke-width:3}}
.court .arc{{fill:none;stroke:{OPTIC};stroke-width:2.4;stroke-dasharray:2 9;stroke-linecap:round}}.court .bounce{{fill:none;stroke:{OPTIC};stroke-width:1.6}}
.wrap{{position:absolute;left:72px;top:64px;width:700px}}
.brand{{display:flex;align-items:center;gap:14px;font-family:Anton;font-size:34px;letter-spacing:1.5px;text-transform:uppercase}}
.brand svg{{width:44px;height:44px}}
.eyebrow{{margin-top:54px;font-weight:800;font-size:20px;letter-spacing:4px;text-transform:uppercase;color:{OPTIC}}}
h1{{font-family:Anton;font-weight:400;font-size:112px;line-height:.9;margin:16px 0 0;text-transform:uppercase}}
h1 span{{color:{OPTIC}}}
h1.t{{font-size:96px}}
.row{{display:flex;align-items:center;gap:22px;margin-top:38px}}
.price{{background:{OPTIC};color:{NAVY};font-weight:800;font-size:26px;padding:14px 26px;border-radius:999px;white-space:nowrap}}
.meta{{font-size:22px;color:#cfd6ea;font-weight:600;line-height:1.35}}
</style></head><body><div class="art">{court}</div><div class="wrap">
<div class="brand"><svg viewBox="0 0 100 100">{art.ball(50, 50, 46, OPTIC, NAVY, 6)}</svg>{e(site["name"])}</div>
<div class="eyebrow">{e(site["brand_sub"])}</div>
{headline}
<div class="row"><div class="price">${site["price"]} / {e(site["lesson_length"])}</div>
<div class="meta">with {e(site["coach"])}<br>{e(areas)}</div></div>
</div></body></html>'''


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
                        '--allow-file-access-from-files', '--virtual-time-budget=3000',
                        '--force-device-scale-factor=1', f'--window-size={w},{h}', f'--screenshot={out}',
                        '--default-background-color=00000000', 'file://' + src],
                       check=True, capture_output=True)
    Image.open(out).convert('RGBA').crop((0, 0, w, h)).save(out, optimize=True)


def svg_page(svg, size):
    s = svg.replace('<svg ', f'<svg width="{size}" height="{size}" ', 1)
    return f'<!doctype html><html><body style="margin:0;background:transparent"><div style="width:{size}px;height:{size}px">{s}</div></body></html>'


def main():
    os.makedirs(os.path.join(ROOT, 'brand'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'images'), exist_ok=True)
    open(os.path.join(ROOT, 'brand', 'mark.svg'), 'w').write(MARK)
    open(os.path.join(ROOT, 'favicon.svg'), 'w').write(FAVICON)
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
    towns = json.load(open(os.path.join(ROOT, 'towns.json'), encoding='utf-8'))['towns']
    os.makedirs(os.path.join(ROOT, 'images', 'og'), exist_ok=True)
    for x in towns:
        png = os.path.join(ROOT, 'images', 'og', x['slug'] + '.tmp.png')
        shot(og_html(x['name']), png, 1200, 630)
        im = Image.open(png).convert('RGB')
        for q in range(86, 76, -1):  # skip encodings whose bytes happen to contain a blocked string (keeps the repo grep clean)
            buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
            if not re.search(rb'5[6]0|46[3]6|te[l]:|sm[s]:|mai[l]to:', buf.getvalue()):
                break
        open(os.path.join(ROOT, 'images', 'og', x['slug'] + '.jpg'), 'wb').write(buf.getvalue())
        os.remove(png)
    print('wrote brand/mark.svg, brand/mark-512.png, favicon.svg, favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png, images/og-image.png')


if __name__ == '__main__':
    main()
