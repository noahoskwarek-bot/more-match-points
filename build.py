#!/usr/bin/env python3
"""Static site generator for More Match Points (GitHub Pages, main branch root).

Edit site.json (or src/style.css), then:
    python3 build.py            # write all generated files
    python3 build.py --check    # exit 1 if anything is out of date (run before committing)
BUILD_DATE=YYYY-MM-DD pins the sitemap date (default: today). See README.md.
"""
import datetime, html, json, os, sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DATE = os.environ.get('BUILD_DATE') or datetime.date.today().isoformat()
e = lambda t: html.escape(str(t), quote=True)


def read(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return f.read()


S = json.loads(read('site.json'))
BASE_URL = S['base_url'].rstrip('/')
BASE = urlparse(BASE_URL).path.rstrip('/')   # "/more-match-points" on github.io, "" on a custom domain
CSS = read('src/style.css')
MARK = read('brand/mark.svg').replace('<svg ', '<svg aria-hidden="true" focusable="false" ', 1)
CHECK = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="11" fill="#1b5e20"/>'
         '<path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#c8f03c" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
AREAS = ' · '.join(S['areas']) + ', ' + S['state']
PRICE = f'${S["price"]}'
COACH = {'@type': 'Person', 'name': S['coach'], 'jobTitle': 'PTR Certified Tennis Instructor'}


def u(path=''):
    return f'{BASE}/{path}'


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
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    ld = '' if noindex else f'<script type="application/ld+json">\n{jsonld()}\n</script>'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
{robots}
<meta name="theme-color" content="#1b5e20">
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
{ld}
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top dark"><div class="wrap">
<a class="brand" href="{u()}" aria-label="{e(S['name'])} home">{MARK}<span class="txt"><b>{e(S['name'])}</b><span class="sub">{e(S['brand_sub'])}</span></span></a>
<a class="call" href="{u()}#request">Request a lesson</a>
</div></header>
'''


def foot(sticky=True):
    bar = f'<div class="sticky dark"><a class="btn ball" href="{u()}#request">Request a lesson</a></div>' if sticky else ''
    year = BUILD_DATE[:4]
    return f'''<footer class="dark"><div class="wrap center">
<p><strong>{e(S['name'])}</strong> · {e(S['footer_line'])}</p>
<p>Private tennis lessons in {e(AREAS)}</p>
<p><a href="{u()}#request">Request a lesson</a></p>
<p class="small" style="color:#d7e6d3">© {year} {e(S['name'])}</p>
</div></footer>
{bar}
</body>
</html>
'''


def form():
    if not S.get('form_endpoint'):
        return ''
    skills = ''.join(f'<option>{e(x)}</option>' for x in S['skill_levels'])
    towns = ''.join(f'<option>{e(x)}</option>' for x in S['form_towns'])
    cap = 'true' if S.get('form_captcha', True) else 'false'
    return f'''<form id="request-form" action="{e(S['form_endpoint'])}" method="POST" aria-labelledby="form-title">
<h3 id="form-title">Lesson request</h3>
<input type="hidden" name="_subject" value="{e(S['form_subject'])}">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="{cap}">
<input type="hidden" name="_next" value="{BASE_URL}/thanks/">
<div class="honey" aria-hidden="true"><label for="f-honey">Leave this empty</label><input id="f-honey" type="text" name="_honey" tabindex="-1" autocomplete="off"></div>
<div class="field"><label for="f-name">Name</label><input id="f-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="f-contact">Phone or email <span class="hint">So Lucas can reply to you</span></label><input id="f-contact" name="phone_or_email" type="text" autocomplete="email" inputmode="email" required aria-describedby="f-contact-hint"><span id="f-contact-hint" class="hint">Your details are only used to reply about lessons.</span></div>
<div class="field"><label for="f-skill">Skill level</label><select id="f-skill" name="skill_level" required><option value="">Choose one</option>{skills}</select></div>
<div class="field"><label for="f-town">Town</label><select id="f-town" name="town" required><option value="">Choose one</option>{towns}</select></div>
<div class="field"><label for="f-times">Preferred times <span class="hint">e.g. weekday afternoons, Saturday mornings</span></label><input id="f-times" name="preferred_times" type="text"></div>
<div class="field"><label for="f-msg">Message <span class="hint">Optional: goals, age of the player, anything else</span></label><textarea id="f-msg" name="message" rows="4"></textarea></div>
<button class="btn primary" type="submit">Send lesson request</button>
</form>'''


def index():
    why = ''.join(f'<li>{CHECK}<span>{e(x)}</span></li>' for x in S['why'])
    cards = ''
    for c in S['experience']:
        meta = ' · '.join(x for x in (c['where'], c.get('when')) if x)
        pts = ''.join(f'<li>{e(p)}</li>' for p in c['points'])
        cards += f'<article class="card"><h3>{e(c["title"])}</h3><p class="meta">{e(meta)}</p><ul>{pts}</ul></article>'
    notes = ' · '.join(e(n) for n in S['offer_notes'])
    body = f'''<main id="main">
<section class="hero" aria-labelledby="hero-title"><div class="wrap">
<h1 id="hero-title">{e(S['tagline'])}</h1>
<p class="kicker">{e(S['kicker'])}</p>
<p class="coach">{e(S['coach'])}</p>
<p class="intro">{e(S['intro'])}</p>
<div class="price dark"><strong>{e(PRICE)} / {e(S['lesson_length'])}</strong><span>{notes}</span></div>
<div class="ctas"><a class="btn primary" href="#request">Request a lesson</a></div>
</div></section>
<section class="why" aria-labelledby="why-title"><div class="wrap">
<h2 id="why-title">{e(S['why_title'])}</h2>
<ul>{why}</ul>
</div></section>
<section class="exp" aria-labelledby="exp-title"><div class="wrap">
<h2 id="exp-title">Experience</h2>
<div class="cards">{cards}</div>
</div></section>
<section class="area dark" aria-labelledby="area-title"><div class="wrap">
<h2 id="area-title">Lesson area</h2>
<p>Serving {e(AREAS)}</p>
</div></section>
<section class="book" id="request" aria-labelledby="book-title" tabindex="-1"><div class="wrap">
<h2 id="book-title">{e(S['book_title'])}</h2>
<p class="intro">{e(S['book_text'])}</p>
<p><strong>{e(PRICE)} per {e(S['lesson_length'])}</strong> · {notes}</p>
{form()}
</div></section>
</main>
'''
    return head(S['title'], S['description'], '') + body + foot()


def thanks():
    t = f'Thanks for your lesson request | {S["name"]}'
    body = f'''<main id="main"><section class="hero"><div class="wrap">
<h1>Thanks!</h1>
<p class="intro">Your lesson request was sent. Lucas will get back to you soon to set up a time.</p>
<div class="ctas"><a class="btn primary" href="{u()}">Back to the home page</a></div>
</div></section></main>
'''
    return head(t, 'Your lesson request was sent.', 'thanks/', noindex=True) + body + foot(sticky=False)


def notfound():
    t = f'Page not found | {S["name"]}'
    body = f'''<main id="main"><section class="hero"><div class="wrap">
<h1>Page not found</h1>
<p class="intro">That page doesn’t exist. Private lessons, prices and the request form are on the home page.</p>
<div class="ctas"><a class="btn primary" href="{u()}">Go to the home page</a> <a class="btn ghost" href="{u()}#request">Request a lesson</a></div>
</div></section></main>
'''
    return head(t, S['description'], '404.html', noindex=True) + body + foot(sticky=False)


def outputs():
    return {
        'index.html': index(),
        'thanks/index.html': thanks(),
        '404.html': notfound(),
        'robots.txt': f'User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n',
        'sitemap.xml': ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                        f'<url><loc>{BASE_URL}/</loc><lastmod>{BUILD_DATE}</lastmod></url>\n</urlset>\n'),
        'site.webmanifest': json.dumps({'name': S['name'], 'short_name': S['short_name'], 'start_url': u(), 'scope': u(),
                                        'display': 'browser', 'background_color': '#ffffff', 'theme_color': '#1b5e20',
                                        'icons': [{'src': u('icon-192.png'), 'sizes': '192x192', 'type': 'image/png'},
                                                  {'src': u('icon-512.png'), 'sizes': '512x512', 'type': 'image/png'}]}, indent=1) + '\n',
        '.nojekyll': '',
    }


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
