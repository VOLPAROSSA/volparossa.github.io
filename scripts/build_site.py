#!/usr/bin/env python3
"""Generate committed GitHub Pages HTML with no third-party build dependencies."""
import argparse
from html import escape
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://volparossa.org'
CORE = 'https://github.com/VOLPAROSSA/volparossa'
VERSION = '1.0.0'

def render(text, values):
    return re.sub(r'\{\{(\w+)\}\}', lambda m: str(values[m[1]]) if m[1] in values else m[0], text)

def picture(name, root='', cls='scene', hero=False):
    height = 710 if name == 'worktable' else 1024
    mobile = ''
    if hero:
        mobile = f'<source media="(max-width: 800px)" type="image/avif" srcset="{root}assets/library/hero-mobile.avif"><source media="(max-width: 800px)" type="image/webp" srcset="{root}assets/library/hero-mobile.webp"><source media="(max-width: 800px)" srcset="{root}assets/library/hero-mobile.jpg">'
    modern = f'<source type="image/avif" srcset="{root}assets/library/hero-768.avif 768w, {root}assets/library/hero-1536.avif 1536w" sizes="100vw">' if hero else ''
    attrs = 'fetchpriority="high" loading="eager"' if hero else 'loading="lazy" decoding="async"'
    return f'<picture class="{cls}">{mobile}{modern}<source type="image/webp" srcset="{root}assets/library/{name}-768.webp 768w, {root}assets/library/{name}-1536.webp 1536w" sizes="100vw"><img src="{root}assets/library/{name}-1536.jpg" srcset="{root}assets/library/{name}-768.jpg 768w, {root}assets/library/{name}-1536.jpg 1536w" sizes="100vw" alt="" width="1536" height="{height}" {attrs}></picture>'

def screen(app, cls=''):
    width, height = {'code': (800,557), 'image': (900,307), 'cloud': (1000,324)}[app]
    return f'<img class="screen screen-{app} {cls}" src="assets/upstream/{app}-screen.webp" width="{width}" height="{height}" alt="" loading="lazy" decoding="async">'

def featured(app, preview):
    ident, name, upstream = app['id'], app['name'], app['upstream']
    mobile_width, mobile_height = {'code': (600,560), 'image': (500,470), 'cloud': (486,480)}[ident]
    logo = ''
    if ident == 'code' or preview:
        file = {'code':'opencode','image':'immich','cloud':'opencloud'}[ident]
        logo = f'<img src="assets/upstream/{file}.svg" width="{126 if ident == "cloud" else 30}" height="42" alt="" class="{"wide-logo" if ident == "cloud" else ""}">'
    mark = f'<a class="upstream {"" if logo else "fallback"}" href="{app["upstream_url"]}">{logo}<span>Built on {upstream}</span></a>'
    return f'''<article class="app-card {ident}" aria-labelledby="app-{ident}">
<div class="device-view"><picture class="mobile-device"><source type="image/webp" media="(max-width: 650px)" srcset="assets/library/{ident}-mobile.webp"><img src="assets/library/{ident}-mobile.jpg" width="{mobile_width}" height="{mobile_height}" alt="" loading="lazy" decoding="async"></picture>{screen(ident)}</div>
<div class="app-content"><h3 id="app-{ident}">{name}</h3><p class="tagline">{app['tagline']}</p>{mark}<p class="app-description">{escape(app['description'])}</p><span class="status">{app['status']}</span><a class="button primary" href="{app['publication_url'] if app['published'] else app['repository']}">Explore {name} <span aria-hidden="true">→</span></a><p class="app-destination">Project repository · GitHub ↗</p></div></article>'''

ICONS = {
'Network':'<circle cx="12" cy="5" r="3"/><circle cx="5" cy="20" r="3"/><circle cx="22" cy="20" r="3"/><path d="m10 8-4 9m8-9 7 9M8 20h11"/>',
'Cache':'<path d="M4 7h20v16H4zM4 7l4-4h12l4 4M9 12h10M9 17h7"/>',
'Storage':'<ellipse cx="14" cy="5" rx="10" ry="4"/><path d="M4 5v16c0 5 20 5 20 0V5M4 13c0 5 20 5 20 0"/>',
'Compute':'<path d="m14 2 11 6v13l-11 6L3 21V8zM3 8l11 6 11-6M14 14v13"/>',
'Transactions':'<path d="M3 8h21l-5-5M25 20H4l5 5M24 8l-5 5M4 20l5-5"/>'}

def layers():
    data=[('Network','Protected connections between participants.','network/ROUTING.md'),('Cache','Reuse eligible, verified public content.','services/CONTENT_NETWORK_PROPOSAL.md'),('Storage','Encrypted private fragments and recovery copies.','services/PRIVATE_STORAGE.md'),('Compute','Suitable tasks shared across participating devices.','services/DECENTRALIZED_AGENTS.md'),('Transactions','Transfers and settlement research with test value.','services/TRANSACTION_LAYER.md')]
    return ''.join(f'<article class="layer"><div class="layer-top"><svg viewBox="0 0 28 28" aria-hidden="true">{ICONS[n]}</svg><h3>{n}</h3></div><p>{d}</p><a href="{CORE}/blob/main/docs/{p}">Read the {n.lower()} guide ↗</a></article>' for n,d,p in data)

DOCS=[
('Overview','The purpose, principles and present boundaries.', [('Project introduction',CORE),('Common questions',CORE+'/blob/main/docs/FAQ.md'),('The complete project goal',CORE+'/blob/main/docs/development/GOAL.md')]),
('Getting started','A practical route for contributors and evaluators.', [('Contributor guide',CORE+'/blob/main/CONTRIBUTING.md'),('Build and package',CORE+'/blob/main/docs/development/OPERATIONS.md#build-and-package'),('Community overview',CORE+'/blob/main/docs/community/OVERVIEW.md')]),
('Core architecture','Five layers, one compatible shared service.', [('Architecture',CORE+'/blob/main/docs/architecture/ARCHITECTURE.md'),('Application lifecycle',CORE+'/blob/main/docs/architecture/APPLICATION_LIFECYCLE.md'),('Privacy and trust boundaries',CORE+'/blob/main/docs/privacy/PRIVACY.md')]),
('Applications','The tools, their upstream foundations and current scope.', [('Application guide',CORE+'/blob/main/docs/applications/APPLICATIONS.md'),('Code integration','https://github.com/VOLPAROSSA/volparossa-code/blob/main/docs/OPENCODE.md'),('Image and Cloud storage',CORE+'/blob/main/docs/services/PRIVATE_STORAGE.md')]),
('Development','Build, test and understand the evidence.', [('Implementation status',CORE+'/blob/main/docs/IMPLEMENTATION_STATUS.md'),('Testing guide',CORE+'/blob/main/docs/development/TESTING.md'),('Operations guide',CORE+'/blob/main/docs/development/OPERATIONS.md')]),
('Contributing','Useful first steps, respectful collaboration and support.', [('Contribution guide','https://github.com/VOLPAROSSA/.github/blob/main/CONTRIBUTING.md'),('Discussions',CORE+'/discussions'),('Support the project',CORE+'/blob/main/docs/community/SUPPORTING.md')])]

def doc_cards():
    return ''.join(f'<section class="portal-card"><p class="number">0{i+1} / Reading path</p><h2>{n}</h2><p>{d}</p><ul>'+''.join(f'<li><a href="{u}">{t} · GitHub ↗</a></li>' for t,u in links)+'</ul></section>' for i,(n,d,links) in enumerate(DOCS))

def app_rows(apps):
    rows=[]
    for a in apps:
        up=f'Built on {escape(a["upstream"])}' if a['upstream'] else 'Original research'
        scope=f'<p class="scope">{escape(a["scope"])}</p>' if a.get('scope') else ''
        rows.append(f'<li class="application-row" id="{a["id"]}"><div><h2>{a["name"]}</h2><p class="upstream-line">{up}</p></div><div><p>{escape(a["description"])}</p>{scope}</div><div class="row-action"><span class="status">{a["status"]}</span><a class="text-link" href="{a["publication_url"] if a["published"] else a["repository"]}">Explore {a["name"]} · GitHub ↗</a></div></li>')
    return ''.join(rows)

PAGES = {
'':('home','VOLPAROSSA — Knowledge grows when we share it.','Open applications. Shared infrastructure. Built together. Explore VOLPAROSSA, its developing applications and cooperative Core.'),
'docs/':('docs','Documentation — VOLPAROSSA','Find VOLPAROSSA guides for getting started, Core architecture, applications, development and contributing.'),
'applications/':('applications','Applications — VOLPAROSSA','Explore the VOLPAROSSA application family, its open-source foundations, repositories and honest development boundaries.'),
'contribute/':('contribute','Get involved — VOLPAROSSA','Contribute code, documentation, testing, accessibility feedback or research to VOLPAROSSA.'),
'privacy/':('privacy','Website privacy — VOLPAROSSA','How this static website handles requests, hosting, external links and privacy, without site-added tracking.'),
'accessibility/':('accessibility','Accessibility — VOLPAROSSA','Accessibility goals, supported website features and how to report a barrier.'),
'credits/':('credits','Credits — VOLPAROSSA','Sources and acknowledgements for VOLPAROSSA illustrations, upstream interfaces, trademarks, fonts and code.'),
'404.html':('404','Page not found — VOLPAROSSA','Find your way back to the VOLPAROSSA homepage or central documentation.'),
'examples/volparossa-application/':('example','Application layout example — VOLPAROSSA','A reusable VOLPAROSSA page shell demonstrating local assets beneath a repository subpath.')}

def build(output, preview=False):
    apps=json.loads((ROOT/'site/data/applications.json').read_text())
    for path,(name,title,description) in PAGES.items():
        depth=path.count('/')
        root='../'*depth
        special=name=='404'
        if special: root=ORIGIN+'/'  # Unknown nested 404 paths still load the real assets.
        links={k:root+v for k,v in [('home',''),('docs','docs/'),('applications','applications/'),('contribute','contribute/'),('privacy','privacy/'),('accessibility','accessibility/'),('credits','credits/')]}
        if name=='example': links={k:ORIGIN+'/'+v.removeprefix(root) for k,v in links.items()}
        nav=[('Discover',links['home']+'#discover'),('Applications',links['applications']),('Documentation',links['docs']),('Get involved',links['contribute']),('GitHub ↗','https://github.com/VOLPAROSSA')]
        nav_links=''.join(f'<a href="{u}"'+(' aria-current="page"' if (name=='docs' and label=='Documentation') or (name=='applications' and label=='Applications') or (name=='contribute' and label=='Get involved') else '')+(' class="github-link"' if label.startswith('GitHub') else '')+f'>{label}</a>' for label,u in nav)
        vals=dict(root=root,title=escape(title),description=escape(description),canonical=ORIGIN+'/'+path,body_class='home' if name=='home' else 'interior',nav_links=nav_links,head_extra='<meta name="robots" content="noindex">' if name in ('404','example') or preview else '',**links)
        vals['header']=render((ROOT/'site/templates/header.html').read_text(),vals)
        vals['footer']=render((ROOT/'site/templates/footer.html').read_text(),vals)
        vals.update(hero_picture=picture('hero',hero=True),worktable_picture=picture('worktable',cls='table-scene')+'<div class="panorama-screens" aria-hidden="true">'+''.join(screen(a) for a in ('code','image','cloud'))+'</div>',shared_picture=picture('shared'),chapter_picture=picture('chapter'),featured_apps=''.join(featured(a,preview) for a in apps if a.get('featured')),layers=layers(),doc_cards=doc_cards(),application_rows=app_rows(apps))
        vals['content']=render((ROOT/f'site/pages/{name}.html').read_text(),vals)
        text=render((ROOT/'site/templates/layout.html').read_text(),vals)
        text=text.replace('↗', '<svg class="external-icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12 12 4M4 4h8v8"/></svg>')
        if re.search(r'\{\{\w+\}\}',text): raise ValueError('Unexpanded template '+name)
        target=output/(path if path.endswith('.html') else path+'index.html')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n')
    paths=[p for p in PAGES if p not in ('404.html','examples/volparossa-application/')]
    (output/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{ORIGIN}/{p}</loc><lastmod>2026-10-30</lastmod></url>\n' for p in paths)+'</urlset>\n')
    if output!=ROOT:
        shutil.copytree(ROOT/'assets',output/'assets',dirs_exist_ok=True)
        for name in ['LICENSE','.nojekyll','favicon.ico','robots.txt']: shutil.copy2(ROOT/name,output/name)
    print(f'Generated {len(PAGES)} pages; shared design v{VERSION}; brands={"review" if preview else "publication fallbacks"}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT)
    parser.add_argument('--preview-brands',action='store_true',help='Review original supplied marks; does not grant public logo permission.')
    args=parser.parse_args();build(args.output.resolve(),args.preview_brands)
