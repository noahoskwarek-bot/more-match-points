#!/usr/bin/env python3
"""Sanity checks for the built site: JSON-LD parses, required nodes exist, no reviews/ratings/phone/email in schema,
unique titles + descriptions, canonical = sitemap URL, one H1 per page, alt text on images, unique town copy word counts."""
import glob, json, os, re, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, 'site.json')))
TOWNS = json.load(open(os.path.join(ROOT, 'towns.json')))['towns']
base = S['base_url'].rstrip('/')
sitemap = re.findall(r'<loc>([^<]+)</loc>', open(os.path.join(ROOT, 'sitemap.xml')).read())
errors, titles, descs = [], {}, {}
def walk(n, f):
    if isinstance(n, dict):
        f(n); [walk(v, f) for v in n.values()]
    elif isinstance(n, list):
        [walk(v, f) for v in n]
for path in sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)):
    rel = os.path.relpath(path, ROOT).replace('index.html', '')
    if rel.startswith('thanks'):
        continue
    h = open(path, encoding='utf-8').read()
    url = base + '/' + rel
    t = html.unescape(re.search(r'<title>(.*?)</title>', h).group(1))
    d = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', h).group(1))
    c = re.search(r'<link rel="canonical" href="([^"]+)"', h).group(1)
    titles.setdefault(t, []).append(rel); descs.setdefault(d, []).append(rel)
    if c != url: errors.append(f'{rel}: canonical {c} != {url}')
    if url not in sitemap: errors.append(f'{rel}: not in sitemap')
    if h.count('<h1') != 1: errors.append(f'{rel}: {h.count("<h1")} h1')
    for img in re.findall(r'<img [^>]*>', h):
        if 'alt="' not in img: errors.append(f'{rel}: img without alt')
    if not (50 <= len(d) <= 170): errors.append(f'{rel}: description length {len(d)}')
    if len(t) > 75: errors.append(f'{rel}: title length {len(t)}')
    types = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            data = json.loads(block)
        except Exception as ex:
            errors.append(f'{rel}: JSON-LD parse error {ex}'); continue
        def chk(n):
            ty = n.get('@type')
            if ty: types.extend(ty if isinstance(ty, list) else [ty])
            for bad in ('telephone', 'email', 'review', 'aggregateRating'):
                if bad in n: errors.append(f'{rel}: schema has {bad}')
            if ty in ('Review', 'AggregateRating'): errors.append(f'{rel}: schema {ty}')
        walk(data, chk)
    need = {'LocalBusiness', 'Person', 'Offer', 'UnitPriceSpecification'}
    if rel != '': need |= {'BreadcrumbList'}
    if rel == 'about/': need |= {'ProfilePage', 'EducationalOccupationalCredential'}
    prices = set(re.findall(r'"price": "([^"]+)"', h))
    if prices != {str(S['price'])}: errors.append(f'{rel}: schema prices {prices} != {S["price"]}')
    if not re.search(r'<a class="dd-link" href="/tennis-lessons/"', h) or not re.search(r'<a class="dd-link" href="/about/"', h):
        errors.append(f'{rel}: no-JS nav links to /tennis-lessons/ and /about/ missing')
    if rel == 'faq/': need |= {'FAQPage', 'Question', 'Answer'}
    if rel.startswith('tennis-lessons/') and rel != 'tennis-lessons/': need |= {'Service'}
    miss = need - set(types)
    if miss: errors.append(f'{rel}: missing schema {sorted(miss)}')
    if rel == '':
        cities = sorted(re.findall(r'"name": "([A-Za-z]+), CT"', h))
        if set(cities) != {x['name'] for x in TOWNS}: errors.append(f'home: areaServed has {len(set(cities))} towns, expected {len(TOWNS)}')
    print(f'{rel or "/":32} {len(t):3}c title  {len(d):3}c desc  schema: {",".join(sorted(set(types)))}')
for k, v in list(titles.items()) + list(descs.items()):
    if len(v) > 1: errors.append(f'duplicate title/description on {v}: {k[:60]}')
words = {}
for x in TOWNS:
    words[x['name']] = len(re.findall(r"[\w'#$-]+", ' '.join([x['lede']] + x['body'])))
    if not 150 <= words[x['name']] <= 300: errors.append(f'{x["name"]}: {words[x["name"]]} words')
print('unique town copy words:', words)
# rough uniqueness: share of 5-word shingles a town page shares with any other town
def sh(x):
    w = re.findall(r"[a-z0-9']+", ' '.join([x['lede']] + x['body']).lower())
    return {' '.join(w[i:i + 5]) for i in range(len(w) - 4)}
for x in TOWNS:
    a = sh(x); other = set().union(*[sh(y) for y in TOWNS if y is not x])
    print(f'  {x["name"]:11} shared 5-word phrases with other towns: {100 * len(a & other) / len(a):.0f}%')
print('sitemap:', len(sitemap), 'urls')
if errors:
    print('\n'.join('ERROR ' + e for e in errors)); sys.exit(1)
print('OK')
