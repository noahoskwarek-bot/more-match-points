#!/usr/bin/env python3
"""Static site generator for More Match Points (GitHub Pages, main branch root, custom domain from site.json base_url).

Edit site.json (or src/style.css, src/site.js, tools/art.py), then:
    python3 build.py            # write all generated files
    python3 build.py --check    # exit 1 if anything is out of date (run before committing)
BUILD_DATE=YYYY-MM-DD pins the sitemap date (default: today). See README.md.
"""
import datetime, html, json, os, sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import art  # noqa: E402

BUILD_DATE = os.environ.get('BUILD_DATE') or datetime.date.today().isoformat()
e = lambda t: html.escape(str(t), quote=True)


def read(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return f.read()


S = json.loads(read('site.json'))
BASE_URL = S['base_url'].rstrip('/')
HOST = urlparse(BASE_URL).hostname
BASE = urlparse(BASE_URL).path.rstrip('/')   # "" on the custom domain, "/<repo>" on a github.io project URL
AREAS = ' · '.join(S['areas']) + ', ' + S['state']
PRICE = f'${S["price"]}'
COACH = {'@type': 'Person', 'name': S['coach'], 'jobTitle': 'PTR Certified Tennis Instructor'}
FONT_CSS = '''@font-face{font-family:"Anton";font-style:normal;font-weight:400;font-display:swap;src:url(%(b)s/fonts/anton-latin.woff2) format("woff2")}
@font-face{font-family:"Inter";font-style:normal;font-weight:400 800;font-display:swap;src:url(%(b)s/fonts/inter-latin-var.woff2) format("woff2")}
'''


def u(path=''):
    return f'{BASE}/{path}'


def css():
    return FONT_CSS % {'b': BASE} + read('src/style.css')


def mark(cls='mark'):
    return (f'<svg class="{cls}" viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
            f'{art.ball(50, 50, 46, art.OPTIC, art.NAVY, 6)}</svg>')


ARROW = '<svg class="arr" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
TICK = '<svg class="tick" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def jsonld():
    data = {
        '@context': 'https://schema.org',
        '@type': ['LocalBusiness', 'SportsActivityLocation'],
        '@id': BASE_URL + '/#business',
        'name': S['name'],
        'description': S['description'],
        'url': BASE_URL + '/',
        'image': BASE_URL + '/images/og-image.png',
        'logo': BASE_URL + '/icon-512.png',
        'priceRange': f'{PRICE} per {S["lesson_length"]}',
        'areaServed': [{'@type': 'City', 'name': f'{c}, {S["state"]}'} for c in S['area_cities']],
        'address': {'@type': 'PostalAddress', 'addressLocality': S['area_cities'][0], 'addressRegion': S['state'], 'addressCountry': 'US'},
        'founder': COACH,
        'employee': COACH,
        'slogan': S['tagline'],
        'makesOffer': {'@type': 'Offer', 'name': f'1-on-1 private tennis lesson ({S["lesson_length"]})',
                       'price': str(S['price']), 'priceCurrency': 'USD'},
    }
    return json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')


def head(title, desc, path, noindex=False):
    canon = BASE_URL + '/' + path
    robots = '<meta name="robots" content="noindex">\n' if noindex else ''
    ld = '' if noindex else f'<script type="application/ld+json">\n{jsonld()}\n</script>\n'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
{robots}<meta name="theme-color" content="{art.NAVY}">
<meta name="color-scheme" content="dark light">
<link rel="preload" href="{u('fonts/anton-latin.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{u('fonts/inter-latin-var.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="icon" href="{u('favicon.ico')}" sizes="any">
<link rel="icon" href="{u('favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{u('apple-touch-icon.png')}">
<link rel="manifest" href="{u('site.webmanifest')}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(S['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{BASE_URL}/images/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(S['name'])}: private tennis lessons with {e(S['coach'])}, {e(PRICE)} per {e(S['lesson_length'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE_URL}/images/og-image.png">
{ld}<style>{css()}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="brand" href="{u()}">{mark()}<span class="word">{e(S['name'])}</span></a>
<nav class="nav" aria-label="Sections"><a href="{u()}#credentials">Credentials</a><a href="{u()}#how">How it works</a><a href="{u()}#pricing">Pricing</a><a href="{u()}#area">Area</a></nav>
<a class="btn optic sm hdr-cta" href="{u()}#request">Request a lesson</a>
</div></header>
'''


def foot(sticky=True):
    bar = f'<div class="sticky" id="sticky"><a class="btn optic block" href="{u()}#request">Request a lesson {ARROW}</a></div>\n' if sticky else ''
    year = BUILD_DATE[:4]
    return f'''<footer class="foot"><div class="wrap">
<div class="foot-brand">{mark()}<div><p class="word">{e(S['name'])}</p><p>{e(S['footer_line'])}</p></div></div>
<p class="foot-area">Private tennis lessons in {e(AREAS)}</p>
<p><a class="foot-cta" href="{u()}#request">Request a lesson {ARROW}</a></p>
<p class="fine">© {year} {e(S['name'])}</p>
</div></footer>
{bar}<script>{read('src/site.js')}</script>
</body>
</html>
'''


def form():
    if not S.get('form_endpoint'):
        return ''
    skills = ''.join(f'<option>{e(x)}</option>' for x in S['skill_levels'])
    towns = ''.join(f'<option>{e(x)}</option>' for x in S['form_towns'])
    cap = 'true' if S.get('form_captcha', True) else 'false'
    return f'''<form class="form" id="request-form" action="{e(S['form_endpoint'])}" method="POST" aria-labelledby="form-title">
<h3 id="form-title">Lesson request</h3>
<input type="hidden" name="_subject" value="{e(S['form_subject'])}">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="{cap}">
<input type="hidden" name="_next" value="{BASE_URL}/thanks/">
<div class="honey" aria-hidden="true"><label for="f-honey">Leave this empty</label><input id="f-honey" type="text" name="_honey" tabindex="-1" autocomplete="off"></div>
<div class="grid2">
<div class="field"><label for="f-name">Name</label><input id="f-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="f-contact">Phone or email</label><input id="f-contact" name="phone_or_email" type="text" autocomplete="email" inputmode="email" required aria-describedby="f-contact-hint"><span id="f-contact-hint" class="hint">Only used to reply about lessons.</span></div>
<div class="field"><label for="f-skill">Skill level</label><select id="f-skill" name="skill_level" required><option value="">Choose one</option>{skills}</select></div>
<div class="field"><label for="f-town">Town</label><select id="f-town" name="town" required><option value="">Choose one</option>{towns}</select></div>
</div>
<div class="field"><label for="f-times">Preferred times <span class="hint">e.g. weekday afternoons, Saturday mornings</span></label><input id="f-times" name="preferred_times" type="text"></div>
<div class="field"><label for="f-msg">Message <span class="hint">Optional: goals, age of the player, anything else</span></label><textarea id="f-msg" name="message" rows="4"></textarea></div>
<button class="btn optic block" type="submit">Send lesson request {ARROW}</button>
</form>'''


def hero_art():
    if S.get('hero_photo'):
        alt = S.get('hero_photo_alt') or f'{S["coach"]} playing tennis'
        return (f'<figure class="hero-art photo"><img src="{u(S["hero_photo"])}" alt="{e(alt)}" width="1200" height="1400" '
                f'fetchpriority="high" decoding="async"></figure>')
    return (f'<figure class="hero-art">{art.court_svg("court")}'
            f'<figcaption class="art-tag"><span>1-on-1</span> Private lessons</figcaption></figure>')


def index():
    lines = S['hero_lines']
    hi = len(lines) - int(S.get('hero_highlight', 1))
    h1 = ''.join(f'<span class="ln{" hi" if i >= hi else ""}">{e(x)}</span>' for i, x in enumerate(lines))
    stats = ''.join(f'<li class="stat reveal"><span class="big">{e(s["big"])}</span><span class="lbl">{e(s["label"])}</span>'
                    f'<span class="sub">{e(s["sub"])}</span></li>' for s in S['stats'])
    cards = ''
    for c in S['experience']:
        meta = ' · '.join(x for x in (c['where'], c.get('when')) if x)
        pts = ''.join(f'<li>{e(p)}</li>' for p in c['points'])
        cards += (f'<article class="xp reveal"><p class="tag">{e(c["tag"])}</p><h3>{e(c["title"])}</h3>'
                  f'<p class="meta">{e(meta)}</p><ul>{pts}</ul></article>')
    steps = ''.join(f'<li class="step reveal"><span class="num">0{i + 1}</span><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></li>'
                    for i, s in enumerate(S['steps']))
    ppts = ''.join(f'<li>{TICK}{e(p)}</li>' for p in S['price_points'])
    towns = ''.join(f'<li>{e(a)}</li>' for a in S['areas'])
    labels = {'Southbury': 'Southbury', 'Middlebury': 'Middlebury', 'Waterbury': 'Greater Waterbury'}
    body = f'''<main id="main">
<section class="hero" aria-labelledby="hero-title"><div class="wrap hero-grid">
<div class="hero-copy">
<p class="eyebrow"><span class="dotb" aria-hidden="true"></span>{e(S['hero_eyebrow'])}</p>
<h1 id="hero-title">{h1}</h1>
<p class="lede">{e(S['hero_intro'])}</p>
<div class="ctas"><a class="btn optic" href="#request">Request a lesson {ARROW}</a><a class="btn line" href="#pricing">{e(PRICE)} / hour</a></div>
<p class="meta-row"><span class="m-price">{e(PRICE)} / {e(S['lesson_length'])}</span><span>{e(S['offer_notes'][0])}</span><span>{e(S['offer_notes'][1])}</span><span>{e(AREAS)}</span></p>
</div>
{hero_art()}
</div></section>
<section class="stats" id="credentials" aria-labelledby="cred-title"><div class="wrap">
<h2 id="cred-title" class="sr">Why train with Lucas</h2>
<ul class="stat-row">{stats}</ul>
</div></section>
<section class="light xp-sec" aria-labelledby="xp-title"><div class="wrap">
<div class="sec-head reveal"><p class="kicker">{e(S['why_title'])}</p><h2 id="xp-title">Experience on court</h2></div>
<div class="xp-grid">{cards}</div>
</div></section>
<section class="how" id="how" aria-labelledby="how-title"><div class="wrap">
<div class="sec-head reveal"><p class="kicker">How it works</p><h2 id="how-title">Request. Confirm. Play.</h2></div>
<ol class="steps">{steps}</ol>
</div></section>
<section class="light price-sec" id="pricing" aria-labelledby="price-title"><div class="wrap price-grid">
<div class="sec-head reveal"><p class="kicker">Pricing</p><h2 id="price-title">One simple rate.</h2>
<p class="body">No packages to figure out. Every lesson is a full hour, 1-on-1 with Lucas.</p></div>
<div class="price-card reveal">
<p class="pc-tag">Private lesson</p>
<p class="amount"><span class="cur">$</span>{e(S['price'])}</p>
<p class="per">per {e(S['lesson_length'])}</p>
<ul class="pc-list">{ppts}</ul>
<a class="btn optic block" href="#request">Request a lesson {ARROW}</a>
</div>
</div></section>
<section class="area" id="area" aria-labelledby="area-title"><div class="wrap area-grid">
<div class="sec-head reveal"><p class="kicker">Lesson area</p><h2 id="area-title">Lessons close to home.</h2>
<ul class="towns">{towns}</ul><p class="body">Connecticut. Pick your town on the request form.</p></div>
<div class="area-box reveal">{art.area_svg(labels)}</div>
</div></section>
<section class="book" id="request" aria-labelledby="book-title" tabindex="-1"><div class="wrap book-grid">
<div class="sec-head"><p class="kicker">Book</p><h2 id="book-title">{e(S['book_title'])}</h2>
<p class="body">{e(S['book_text'])}</p>
<p class="book-price"><strong>{e(PRICE)}</strong> per {e(S['lesson_length'])} · {e(' · '.join(S['offer_notes']))}</p></div>
{form()}
</div></section>
</main>
'''
    return head(S['title'], S['description'], '') + body + foot()


def simple(title, desc, path, h, text, buttons):
    body = f'''<main id="main"><section class="hero simple"><div class="wrap">
<p class="eyebrow"><span class="dotb" aria-hidden="true"></span>{e(S['name'])}</p>
<h1><span class="ln hi">{e(h)}</span></h1>
<p class="lede">{e(text)}</p>
<div class="ctas">{buttons}</div>
</div></section></main>
'''
    return head(title, desc, path, noindex=True) + body + foot(sticky=False)


def outputs():
    out = {
        'index.html': index(),
        'thanks/index.html': simple(f'Thanks for your lesson request | {S["name"]}', 'Your lesson request was sent.', 'thanks/',
                                    'Thanks!', 'Your lesson request was sent. Lucas will get back to you soon to set up a time.',
                                    f'<a class="btn optic" href="{u()}">Back to the home page {ARROW}</a>'),
        '404.html': simple(f'Page not found | {S["name"]}', S['description'], '404.html', 'Out of bounds.',
                           'That page doesn’t exist. Lessons, pricing and the request form are on the home page.',
                           f'<a class="btn optic" href="{u()}">Go to the home page {ARROW}</a><a class="btn line" href="{u()}#request">Request a lesson</a>'),
        'robots.txt': f'User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n',
        'sitemap.xml': ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                        f'<url><loc>{BASE_URL}/</loc><lastmod>{BUILD_DATE}</lastmod></url>\n</urlset>\n'),
        'site.webmanifest': json.dumps({'name': S['name'], 'short_name': S['short_name'], 'start_url': u(), 'scope': u(),
                                        'display': 'browser', 'background_color': art.NAVY, 'theme_color': art.NAVY,
                                        'icons': [{'src': u('icon-192.png'), 'sizes': '192x192', 'type': 'image/png'},
                                                  {'src': u('icon-512.png'), 'sizes': '512x512', 'type': 'image/png'}]}, indent=1) + '\n',
        '.nojekyll': '',
    }
    if HOST and not HOST.endswith('github.io'):
        out['CNAME'] = HOST + '\n'
    return out


def main():
    check = '--check' in sys.argv
    stale = []
    for path, text in outputs().items():
        full = os.path.join(ROOT, path)
        old = open(full, encoding='utf-8').read() if os.path.exists(full) else None
        if old == text:
            continue
        if check:
            stale.append(path)
        else:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'w', encoding='utf-8') as f:
                f.write(text)
            print('wrote', path)
    if check:
        if stale:
            sys.exit('out of date (run python3 build.py): ' + ', '.join(stale))
        print('build is up to date')


if __name__ == '__main__':
    main()
