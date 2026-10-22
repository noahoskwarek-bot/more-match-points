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
TOWNS = json.loads(read('towns.json'))['towns']
PRICE = f'${S["price"]}'
TOWN_LIST = ', '.join(x['name'] for x in TOWNS[:-1]) + ' and ' + TOWNS[-1]['name']


def fill(v):
    """{price} and {towns} in any site.json / towns.json text -> the single price setting / every town."""
    if isinstance(v, str):
        return v.replace('{price}', PRICE).replace('{towns}', TOWN_LIST)
    if isinstance(v, list):
        return [fill(x) for x in v]
    if isinstance(v, dict):
        return {k: fill(x) for k, x in v.items()}
    return v


S, TOWNS = fill(S), fill(TOWNS)
BASE_URL = S['base_url'].rstrip('/')
HOST = urlparse(BASE_URL).hostname
BASE = urlparse(BASE_URL).path.rstrip('/')   # "" on the custom domain, "/<repo>" on a github.io project URL
AREAS = S['area_line']
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


BIZ_ID = BASE_URL + '/#business'
PERSON_ID = BASE_URL + '/about/#lucas'


def offer(area=None):
    o = {'@type': 'Offer', 'name': f'1-on-1 private tennis lesson ({S["lesson_length"]})',
         'price': str(S['price']), 'priceCurrency': 'USD', 'url': BASE_URL + '/#request',
         'priceSpecification': {'@type': 'UnitPriceSpecification', 'price': str(S['price']), 'priceCurrency': 'USD',
                                'unitCode': 'HUR', 'unitText': 'hour',
                                'referenceQuantity': {'@type': 'QuantitativeValue', 'value': 1, 'unitCode': 'HUR'}}}
    if area:
        o['areaServed'] = area
    return o


def city(name):
    return {'@type': 'City', 'name': f'{name}, {S["state"]}',
            'containedInPlace': {'@type': 'State', 'name': 'Connecticut'}}


def base_graph():
    biz = {
        '@type': ['LocalBusiness', 'SportsActivityLocation'],
        '@id': BIZ_ID,
        'name': S['name'],
        'description': S['description'],
        'url': BASE_URL + '/',
        'image': BASE_URL + '/images/og-image.png',
        'logo': BASE_URL + '/icon-512.png',
        'priceRange': f'{PRICE} per {S["lesson_length"]}',
        'areaServed': [city(c) for c in S['area_cities']],
        'address': {'@type': 'PostalAddress', 'addressLocality': S['area_cities'][0], 'addressRegion': S['state'], 'addressCountry': 'US'},
        'founder': {'@type': 'Person', '@id': PERSON_ID, 'name': S['coach'], 'url': BASE_URL + '/about/'},
        'employee': {'@id': PERSON_ID},
        'slogan': S['tagline'],
        'knowsAbout': ['Tennis', 'Private tennis lessons', 'Tennis lessons for kids', 'Beginner tennis lessons'],
        'makesOffer': offer(),
    }
    return [biz]


def person_node():
    return {
        '@type': 'Person',
        '@id': PERSON_ID,
        'name': S['coach'],
        'url': BASE_URL + '/about/',
        'jobTitle': 'PTR Certified Tennis Instructor',
        'worksFor': {'@id': BIZ_ID},
        'knowsAbout': ['Tennis', 'Tennis instruction', 'Professional Tennis Registry (PTR) certification', 'USTA tournament tennis'],
        'hasCredential': {'@type': 'EducationalOccupationalCredential', 'name': 'PTR Certified Tennis Instructor',
                          'credentialCategory': 'certification',
                          'recognizedBy': {'@type': 'Organization', 'name': 'Professional Tennis Registry (PTR)'}},
        'memberOf': {'@type': 'SportsTeam', 'name': 'Pomperaug High School varsity tennis', 'sport': 'Tennis'},
    }


def crumbs(items):
    """items: [(name, path)] from Home to the current page."""
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': BASE_URL + '/' + p} for i, (n, p) in enumerate(items)]}


def jsonld(extra=()):
    data = {'@context': 'https://schema.org', '@graph': base_graph() + list(extra)}
    return json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')


def head(title, desc, path, noindex=False, ld_extra=(), og=None):
    canon = BASE_URL + '/' + path
    robots = '<meta name="robots" content="noindex">\n' if noindex else ''
    ld = '' if noindex else f'<script type="application/ld+json">\n{jsonld(ld_extra)}\n</script>\n'
    og = og or 'images/og-image.png'
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
<meta property="og:image" content="{BASE_URL}/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(S['name'])}: private tennis lessons with {e(S['coach'])}, {e(PRICE)} per {e(S['lesson_length'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE_URL}/{og}">
{ld}<style>{css()}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top" id="top"><div class="wrap">
<a class="brand" href="{u()}">{mark()}<span class="word">{e(S['name'])}</span></a>
{nav()}
<a class="btn optic sm hdr-cta" href="{u()}#request">Request a lesson</a>
</div></header>
'''


CHEV = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def dropdown(key, label, href, links):
    """Disclosure menu. Without JS the label is a plain link to href; site.js swaps in the button."""
    items = ''.join(f'<li><a href="{h}">{e(n)}</a></li>' for n, h in links)
    return (f'<li class="dd" data-dd="{key}"><a class="dd-link" href="{href}">{e(label)}</a>'
            f'<button class="dd-btn" type="button" aria-expanded="false" aria-controls="dd-{key}" hidden>{e(label)}{CHEV}</button>'
            f'<ul class="dd-menu dd-{key}" id="dd-{key}">{items}</ul></li>')


def nav():
    locs = [(f'{x["name"]}, CT', town_url(x)) for x in TOWNS] + [('All locations', u('tennis-lessons/'))]
    about = [('About Lucas', u('about/')), ('FAQ', u('faq/'))]
    return (f'<button class="burger" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menu" hidden>'
            f'<span class="bars" aria-hidden="true"><i></i><i></i><i></i></span></button>'
            f'<nav class="nav" id="site-nav" aria-label="Main"><ul class="nav-list">'
            f'<li><a href="{u()}#how">How it works</a></li><li><a href="{u()}#pricing">Pricing</a></li>'
            f'{dropdown("loc", "Locations", u("tennis-lessons/"), locs)}{dropdown("about", "About", u("about/"), about)}'
            f'<li class="nav-cta"><a class="btn optic block" href="{u()}#request">Request a lesson {ARROW}</a></li>'
            f'</ul></nav>')


def foot(sticky=True):
    bar = f'<div class="sticky" id="sticky"><a class="btn optic block" href="{u()}#request">Request a lesson {ARROW}</a></div>\n' if sticky else ''
    year = BUILD_DATE[:4]
    return f'''<footer class="foot"><div class="wrap">
<div class="foot-brand">{mark()}<div><p class="word">{e(S['name'])}</p><p>{e(S['footer_line'])}</p></div></div>
<p class="foot-area">Private tennis lessons in {e(AREAS)}</p>
<nav class="foot-towns" aria-label="Tennis lessons by town"><p class="foot-h"><a href="{u('tennis-lessons/')}">Locations</a></p><ul>{''.join(f'<li><a href="{u("tennis-lessons/" + x["slug"] + "/")}">{e(x["name"])}</a></li>' for x in TOWNS)}</ul></nav>
<p class="foot-links"><a href="{u('about/')}">About Lucas</a><a href="{u('faq/')}">FAQ</a><a href="{u('tennis-lessons/')}">All locations</a></p>
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
    return f'''<form class="form" id="request-form" action="{e(S['form_endpoint'])}" method="POST" aria-labelledby="form-title">
<h3 id="form-title">Lesson request</h3>
<input type="hidden" name="_subject" value="{e(S['form_subject'])}">
<div class="honey" aria-hidden="true"><label for="f-gotcha">Leave this empty</label><input id="f-gotcha" type="text" name="_gotcha" tabindex="-1" autocomplete="off"></div>
<div class="grid2">
<div class="field"><label for="f-name">Name</label><input id="f-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="f-contact">Phone or email</label><input id="f-contact" name="phone_or_email" type="text" autocomplete="email" inputmode="email" required aria-describedby="f-contact-hint"><span id="f-contact-hint" class="hint">Only used to reply about lessons.</span></div>
<div class="field"><label for="f-skill">Skill level</label><select id="f-skill" name="skill_level" required><option value="">Choose one</option>{skills}</select></div>
<div class="field"><label for="f-town">Town</label><select id="f-town" name="town" required><option value="">Choose one</option>{towns}</select></div>
</div>
<div class="field"><label for="f-times">Preferred times <span class="hint">e.g. weekday afternoons, Saturday mornings</span></label><input id="f-times" name="preferred_times" type="text"></div>
<div class="field"><label for="f-msg">Message <span class="hint">Optional: goals, age of the player, anything else</span></label><textarea id="f-msg" name="message" rows="4"></textarea></div>
<p class="form-err" id="form-err" role="alert" tabindex="-1" hidden>Sorry, your request didn't go through. Please check your connection and try again in a moment.</p>
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
    stats = stat_items()
    steps = ''.join(f'<li class="step reveal"><span class="num">0{i + 1}</span><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></li>'
                    for i, s in enumerate(S['steps']))
    ppts = ''.join(f'<li>{TICK}{e(p)}</li>' for p in S['price_points'])
    towns = town_chips()
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
<p class="stat-more"><a class="text-link" href="{u('about/')}">About Lucas and his experience {ARROW}</a></p>
</div></section>
<section class="how" id="how" aria-labelledby="how-title"><div class="wrap">
<div class="sec-head reveal"><p class="kicker">How it works</p><h2 id="how-title">Request. Confirm. Play.</h2></div>
<ol class="steps">{steps}</ol>
</div></section>
<section class="light price-sec" id="pricing" aria-labelledby="price-title"><div class="wrap price-grid">
<div class="sec-head reveal"><p class="kicker">Pricing</p><h2 id="price-title">One simple rate.</h2>
<p class="body">{e(S['price_intro'])}</p></div>
<div class="price-card reveal">
<p class="pc-tag">Private lesson</p>
<p class="amount"><span class="cur">$</span>{e(S['price'])}</p>
<p class="per">per {e(S['lesson_length'])}</p>
<ul class="pc-list">{ppts}</ul>
<a class="btn optic block" href="#request">Request a lesson {ARROW}</a>
</div>
</div></section>
<section class="area" id="area" aria-labelledby="area-title"><div class="wrap area-grid">
<div class="sec-head reveal"><p class="kicker">Lesson area</p><h2 id="area-title">{e(S['area_title'])}</h2>
<p class="body">{e(S['area_intro'])}</p>{towns}
<p class="more"><a class="text-link" href="{u('tennis-lessons/')}">All locations {ARROW}</a></p></div>
<div class="area-box reveal">{art.area_svg(TOWNS)}</div>
</div></section>
{reviews_section()}{faq_block()}<section class="book" id="request" aria-labelledby="book-title" tabindex="-1"><div class="wrap book-grid">
<div class="sec-head"><p class="kicker">Book</p><h2 id="book-title">{e(S['book_title'])}</h2>
<p class="body">{e(S['book_text'])}</p>
<p class="book-price"><strong>{e(PRICE)}</strong> per {e(S['lesson_length'])} · {e(' · '.join(S['offer_notes']))}</p></div>
{form()}
</div></section>
</main>
'''
    return head(S['title'], S.get('meta_description', S['description']), '') + body + foot()


def town_url(x):
    return u('tennis-lessons/' + x['slug'] + '/')


def town_chips(exclude=None):
    items = ''.join(f'<li><a href="{town_url(x)}">{e(x["name"])}<span class="sr">, CT tennis lessons</span></a></li>'
                    for x in TOWNS if x['name'] != exclude)
    return f'<ul class="towns links">{items}</ul>'


def faq_items(items):
    return ''.join(f'<details class="qa"><summary><span>{e(f["q"])}</span><span class="pm" aria-hidden="true"></span></summary>'
                   f'<div class="ans"><p>{e(f["a"])}</p></div></details>' for f in items)


def faq_block():
    items = S['faq'][:int(S.get('home_faq_count', 4))]
    return f'''<section class="light faq-sec" id="faq" aria-labelledby="faq-title"><div class="wrap faq-grid">
<div class="sec-head reveal"><p class="kicker">FAQ</p><h2 id="faq-title">Good to know.</h2>
<p class="body">Quick answers about private tennis lessons, from what to bring to tennis lessons for kids.</p>
<p class="more"><a class="text-link" href="{u('faq/')}">All questions {ARROW}</a></p></div>
<div class="faq-list reveal">{faq_items(items)}</div>
</div></section>
'''


def reviews_section():
    revs = [r for r in S.get('reviews', []) if r.get('text') and r.get('name')]
    if not revs:
        return ''
    cards = ''.join(f'<figure class="rev reveal"><blockquote><p>{e(r["text"])}</p></blockquote>'
                    f'<figcaption>{e(r["name"])}{(" · " + e(r["date"])) if r.get("date") else ""}</figcaption></figure>' for r in revs)
    return f'''<section class="reviews" aria-labelledby="rev-title"><div class="wrap">
<div class="sec-head reveal"><p class="kicker">Reviews</p><h2 id="rev-title">From the court.</h2></div>
<div class="rev-grid">{cards}</div>
</div></section>
'''


def crumb_nav(items):
    lis = []
    for i, (n, p) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li><span aria-current="page">{e(n)}</span></li>')
        else:
            lis.append(f'<li><a href="{u(p)}">{e(n)}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def mini_price():
    ppts = ''.join(f'<li>{TICK}{e(p)}</li>' for p in S['price_points'])
    return f'''<aside class="price-card mini" aria-label="Lesson price">
<p class="pc-tag">Private lesson</p>
<p class="amount"><span class="cur">$</span>{e(S['price'])}</p>
<p class="per">per {e(S['lesson_length'])}</p>
<ul class="pc-list">{ppts}</ul>
<a class="btn optic block" href="{u()}#request">Request a lesson {ARROW}</a>
</aside>'''


def page_hero(eyebrow, h1, lede, crumbs_items, buttons=None):
    buttons = buttons or (f'<a class="btn optic" href="{u()}#request">Request a lesson {ARROW}</a>'
                          f'<a class="btn line" href="{u()}#pricing">{e(PRICE)} / hour</a>')
    return f'''<section class="hero page-hero"><div class="wrap">
{crumb_nav(crumbs_items)}
<p class="eyebrow"><span class="dotb" aria-hidden="true"></span>{e(eyebrow)}</p>
<h1 id="page-title">{h1}</h1>
<p class="lede">{e(lede)}</p>
<div class="ctas">{buttons}</div>
</div><div class="bg-court" aria-hidden="true">{art.court_svg('court', ball_on=False)}</div></section>
'''


def town_page(x):
    name = x['name']
    path = f'tennis-lessons/{x["slug"]}/'
    title = f'Private Tennis Lessons in {name}, CT | {S["name"]}'
    desc = x['lede'] if len(x['lede']) > 140 else f'{x["lede"]} Request a lesson online.'
    items = [('Home', ''), ('Tennis lessons', 'tennis-lessons/'), (f'{name}, CT', path)]
    paras = ''.join(f'<p>{e(b)}</p>' for b in x['body'])
    if x.get('courts'):
        li = ''.join(f'<li>{e(c)}</li>' for c in x['courts'])
        courts = (f'<div class="note"><h3>Public courts in {e(name)}</h3><ul>{li}</ul>'
                  f'<p>Listed by the town\u2019s parks and recreation department. Your lesson court is arranged when you book.</p></div>')
    else:
        courts = ('<div class="note"><h3>Where lessons happen</h3>'
                  f'<p>{e(x.get("where_note") or "At a local public court in the area, arranged with you when you book.")}</p></div>')
    service = {'@type': 'Service', '@id': BASE_URL + '/' + path + '#service',
               'name': f'Private tennis lessons in {name}, CT', 'serviceType': 'Private tennis lessons',
               'provider': {'@id': BIZ_ID}, 'areaServed': city(name), 'offers': offer(city(name)),
               'url': BASE_URL + '/' + path}
    h1 = f'<span class="ln">Private tennis lessons in</span> <span class="ln hi">{e(name)}, CT</span>'
    body = f'''<main id="main">
{page_hero(f'Tennis lessons · {name}, CT', h1, x['lede'], items)}
<section class="light town-sec"><div class="wrap town-grid">
<div class="prose reveal"><h2 class="h2s">Tennis lessons in {e(name)}</h2>{paras}{courts}</div>
{mini_price()}
</div></section>
<section class="area near"><div class="wrap">
<div class="sec-head"><p class="kicker">Nearby</p><h2>Other towns I teach in</h2></div>
{town_chips(exclude=name)}
<p class="more"><a class="text-link" href="{u('tennis-lessons/')}">All locations {ARROW}</a> <a class="text-link" href="{u('about/')}">About Lucas {ARROW}</a> <a class="text-link" href="{u('faq/')}">Lesson FAQ {ARROW}</a></p>
</div></section>
</main>
'''
    og = f'images/og/{x["slug"]}.jpg'
    return head(title, desc, path, ld_extra=[crumbs(items), service], og=og) + body + foot()


def towns_index():
    path = 'tennis-lessons/'
    title = f'Tennis Lessons by Town in Connecticut | {S["name"]}'
    desc = (f'Private tennis lessons with a PTR Certified coach in {len(TOWNS)} Connecticut towns, from Greater Waterbury '
            f'to Newtown, Monroe, Redding and Danbury. {PRICE} per hour.')
    items = [('Home', ''), ('Tennis lessons', path)]
    cards = ''.join(f'<li class="tcard reveal"><a href="{town_url(x)}"><span class="tn">{e(x["name"])}, CT</span>'
                    f'<span class="ts">{e(x["lede"])}</span><span class="tg">Tennis lessons in {e(x["name"])} {ARROW}</span></a></li>'
                    for x in TOWNS)
    lst = {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': f'{x["name"]}, CT',
                                                     'url': BASE_URL + town_url(x)} for i, x in enumerate(TOWNS)]}
    h1 = '<span class="ln">Tennis lessons</span> <span class="ln hi">by town.</span>'
    lede = ('Private 1-on-1 tennis lessons from Middlebury, Southbury and Greater Waterbury through Newtown, Monroe, Redding '
            'and Danbury, Connecticut. Your lesson court is arranged with you when you book.')
    body = f'''<main id="main">
{page_hero('Where I teach', h1, lede, items)}
<section class="light"><div class="wrap">
<ul class="tgrid">{cards}</ul>
</div></section>
<section class="area"><div class="wrap area-grid">
<div class="sec-head"><p class="kicker">Lesson area</p><h2>{NUM_WORDS.get(len(TOWNS), len(TOWNS))} towns, one simple rate.</h2>
<p class="body">Every lesson is {e(PRICE)} per {e(S['lesson_length'])}, 1-on-1, with flexible scheduling. Don\u2019t see your town? Choose Other on the request form.</p>
<p class="more"><a class="btn optic" href="{u()}#request">Request a lesson {ARROW}</a></p></div>
<div class="area-box">{art.area_svg(TOWNS)}</div>
</div></section>
</main>
'''
    return head(title, desc, path, ld_extra=[crumbs(items), lst]) + body + foot()


NUM_WORDS = {9: 'Nine', 10: 'Ten', 11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', 15: 'Fifteen'}


def stat_items(reveal=True):
    return ''.join(f'<li class="stat{" reveal" if reveal else ""}"><span class="big">{e(s["big"])}</span><span class="lbl">{e(s["label"])}</span>'
                   f'<span class="sub">{e(s["sub"])}</span></li>' for s in S['stats'])


def xp_cards():
    cards = ''
    for c in S['experience']:
        meta = ' · '.join(x for x in (c['where'], c.get('when')) if x)
        pts = ''.join(f'<li>{e(p)}</li>' for p in c['points'])
        cards += (f'<article class="xp reveal"><p class="tag">{e(c["tag"])}</p><h3>{e(c["title"])}</h3>'
                  f'<p class="meta">{e(meta)}</p><ul>{pts}</ul></article>')
    return cards


def about_page():
    path = 'about/'
    title = f'About Lucas Oskwarek, PTR Certified Tennis Coach | {S["name"]}'
    desc = ('Meet Lucas Oskwarek: PTR Certified tennis instructor, Pomperaug #1 singles, SWC champion, top 30 USTA CT '
            'and Highfield CC kids camp coach.')
    items = [('Home', ''), ('About Lucas', path)]
    prof = {'@type': 'ProfilePage', '@id': BASE_URL + '/about/#page', 'url': BASE_URL + '/about/',
            'name': title, 'mainEntity': {'@id': PERSON_ID}}
    h1 = '<span class="ln">About</span> <span class="ln hi">Lucas.</span>'
    body = f'''<main id="main">
{page_hero('About Lucas', h1, S['about_intro'], items)}
<section class="stats about-stats" aria-labelledby="cred-title"><div class="wrap">
<h2 id="cred-title" class="sr">Credentials</h2>
<ul class="stat-row">{stat_items()}</ul>
</div></section>
<section class="light xp-sec" aria-labelledby="xp-title"><div class="wrap">
<div class="sec-head reveal"><p class="kicker">{e(S['why_title'])}</p><h2 id="xp-title">Experience on court</h2><p class="body">{e(S['xp_intro'])}</p></div>
<div class="xp-grid">{xp_cards()}</div>
</div></section>
<section class="area near"><div class="wrap">
<div class="sec-head"><p class="kicker">Lessons</p><h2>Train with Lucas</h2>
<p class="body">{e(PRICE)} per {e(S['lesson_length'])}, 1-on-1, for kids, teens and adults. {e(AREAS)}.</p></div>
<p class="more"><a class="btn optic" href="{u()}#request">Request a lesson {ARROW}</a> <a class="text-link" href="{u('tennis-lessons/')}">Locations {ARROW}</a> <a class="text-link" href="{u('faq/')}">FAQ {ARROW}</a></p>
</div></section>
</main>
'''
    return head(title, desc, path, ld_extra=[crumbs(items), person_node(), prof]) + body + foot()


def faq_page():
    path = 'faq/'
    title = f'Tennis Lesson FAQ: Price, What to Bring, Kids & Booking | {S["name"]}'
    desc = (f'Tennis lesson questions answered: {PRICE} per 1-hour lesson, what to bring, skill levels, '
            'lessons for kids, where lessons happen, rain and booking.')
    items = [('Home', ''), ('FAQ', path)]
    faq = {'@type': 'FAQPage', '@id': BASE_URL + '/faq/#faq', 'mainEntity': [
        {'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}} for f in S['faq']]}
    h1 = '<span class="ln">Lesson</span> <span class="ln hi">questions.</span>'
    body = f'''<main id="main">
{page_hero('FAQ', h1, 'Everything you need to know before your first private tennis lesson.', items)}
<section class="light faq-sec"><div class="wrap faq-grid">
<div class="sec-head"><p class="kicker">Still wondering?</p><h2>Ask in your request.</h2>
<p class="body">Anything not covered here can go in the message box on the lesson request form.</p>
<p class="more"><a class="btn optic" href="{u()}#request">Request a lesson {ARROW}</a></p></div>
<div class="faq-list">{faq_items(S['faq'])}</div>
</div></section>
<section class="area near"><div class="wrap">
<div class="sec-head"><p class="kicker">Where I teach</p><h2>Tennis lessons by town</h2></div>
{town_chips()}
</div></section>
</main>
'''
    return head(title, desc, path, ld_extra=[crumbs(items), faq]) + body + foot()


def sitemap_paths():
    return [''] + ['tennis-lessons/'] + [f'tennis-lessons/{x["slug"]}/' for x in TOWNS] + ['about/', 'faq/']


def sitemap():
    urls = ''.join(f'<url><loc>{BASE_URL}/{p}</loc><lastmod>{BUILD_DATE}</lastmod></url>\n' for p in sitemap_paths())
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + urls + '</urlset>\n')


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
        'sitemap.xml': sitemap(),
        'tennis-lessons/index.html': towns_index(),
        'faq/index.html': faq_page(),
        'about/index.html': about_page(),
        'site.webmanifest': json.dumps({'name': S['name'], 'short_name': S['short_name'], 'start_url': u(), 'scope': u(),
                                        'display': 'browser', 'background_color': art.NAVY, 'theme_color': art.NAVY,
                                        'icons': [{'src': u('icon-192.png'), 'sizes': '192x192', 'type': 'image/png'},
                                                  {'src': u('icon-512.png'), 'sizes': '512x512', 'type': 'image/png'}]}, indent=1) + '\n',
        '.nojekyll': '',
    }
    for x in TOWNS:
        out[f'tennis-lessons/{x["slug"]}/index.html'] = town_page(x)
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
