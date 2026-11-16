#!/usr/bin/env python3
"""Generate team profiles, homepage cards and shared research-area content."""
from html import escape
import json
from pathlib import Path
import re
from string import Template

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
DATA = SITE / 'data/people'
TEMPLATES = SITE / 'templates/profile'
PLACEHOLDER = 'people/gustavo-rivas-gervilla-cutout.svg'
RESEARCH_ASSET_VERSIONS = {'complex-treatments': 6, 'targeted-learning': 15, 'conformal-inference': 13, 'population-health': 5}

def attr(value):
    return escape(str(value), quote=True)

def links_html(links, prefix, lang):
    labels = {'en': {'orcid':'ORCID profile','scholar':'Google Scholar profile','github':'GitHub profile','linkedin':'LinkedIn profile','email':'Send email'}, 'es': {'orcid':'Perfil de ORCID','scholar':'Perfil de Google Scholar','github':'Perfil de GitHub','linkedin':'Perfil de LinkedIn','email':'Enviar correo'}}
    icons = {'orcid':'orcid.svg','scholar':'google-scholar.svg','github':'github.svg'}
    result = []
    for key in ('orcid','scholar','github','linkedin','email'):
        value = links.get(key)
        if not value:
            continue
        href = 'mailto:' + value if key == 'email' else value
        icon = f'<img src="{prefix}assets/icons/{icons[key]}" alt="">' if key in icons else (TEMPLATES / f'icon-{key}.html').read_text()
        extra = ' profile-icon-email' if key == 'email' else ''
        result.append(f'<a class="profile-icon-link{extra}" href="{attr(href)}" aria-label="{labels[lang][key]}">{icon}</a>')
    if not result:
        return ''
    label = 'Profiles and contact' if lang == 'en' else 'Perfiles y contacto'
    return f'<div class="profile-links" role="group" aria-label="{label}">{"".join(result)}</div>'

def research_content(areas, definitions, prefix, home_href):
    if not areas:
        return '', ''
    single = len(areas) == 1
    choices, panels = [], []
    for key in areas:
        a = definitions[key]
        id_ = 'research-' + key
        version = f'?v={RESEARCH_ASSET_VERSIONS[key]}' if key in RESEARCH_ASSET_VERSIONS else ''
        visual = f'<div class="research-visual"><img src="{prefix}assets/{attr(a["image"])}{version}" alt="" width="300" height="150" loading="lazy"></div>'
        body = a['body'].replace('__HOME__', home_href)
        panel_attr = '' if single else ' data-research-panel'
        panels.append(f'<article class="research-area-detail" id="{id_}"{panel_attr} role="region" tabindex="-1" aria-labelledby="{id_}-title">{visual}<div class="research-area-copy"><h3 id="{id_}-title">{a["title"]}</h3><div class="research-area-body">{body}</div></div></article>')
        if not single:
            choices.append(f'<a class="research-choice" href="#{id_}" data-research-select aria-controls="{id_}">{a["label"]}</a>')
    selector_attr = '' if single else f' data-research-selector data-research-default="research-{attr(areas[0])}" data-research-placement="end"'
    content = panels[0] if single else f'<div class="research-grid">{"".join(choices)}<div class="research-panels" data-research-panels>{"".join(panels)}</div></div>'
    return selector_attr, content

def related_html(areas, definitions, prefix, lang):
    if not areas:
        return ''
    title = 'Related research areas' if lang == 'en' else 'Líneas relacionadas'
    selector_class = '' if len(areas) == 1 else ' research-selector'
    selector_attr, content = research_content(areas, definitions, prefix, '../../index.html')
    top = '<svg class="profile-wave profile-wave-top" viewBox="0 0 1440 80" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="M0 16 C280 16 420 32 700 48 C980 64 1170 64 1440 64 L1440 80 H0 Z"/></svg>'
    end = '<svg class="profile-wave profile-wave-end" viewBox="0 0 1440 80" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="M0 64 C280 64 470 64 740 48 C1010 32 1160 16 1440 16 L1440 80 H0 Z"/></svg>'
    return f'<div class="profile-related-surface">{top}<section class="section wrap section-tight profile-related{selector_class}"{selector_attr}><div class="section-heading"><div><h2>{title}</h2></div></div>{content}</section>{end}</div>'

def render_person(person, lang, definitions):
    slug = person['slug']
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError(f'Invalid slug: {slug}')
    info = person['languages'][lang]
    prefix = '../../' if lang == 'en' else '../../../'
    target = SITE / ('' if lang == 'en' else 'es') / 'team' / slug / 'index.qmd'
    alternate = '../../es/team/' if lang == 'en' else '../../../team/'
    name = info['name']
    image = person.get('photo') or PLACEHOLDER
    if not (SITE/'assets'/image).is_file():
        raise ValueError(f'Image missing: {image}')
    appointments = []
    for a in info.get('appointments', []):
        affiliations = ''.join(f'<li>{escape(x)}</li>' for x in a.get('affiliations', []))
        appointments.append(f'<div class="profile-appointment"><p class="profile-position">{escape(a["position"])}</p><ul class="profile-affiliations">{affiliations}</ul></div>')
    credentials = '<div class="profile-credentials">' + ''.join(appointments) + '</div>' if appointments else ''
    # Bio supports simple HTML for links and emphasis, as in the existing profiles.
    biography = ''.join(f'<p class="profile-bio">{text}</p>' for text in info.get('bio', []))
    markup = Template((TEMPLATES/'layout.html').read_text()).substitute(profile_class='profile-intro-miguel' if slug == 'miguel-luque' else 'profile-intro-standard', photo_class='profile-photo-placeholder' if image.endswith('.svg') else '', photo=prefix+'assets/'+attr(image), photo_alt=attr(('Portrait of ' if lang=='en' else 'Retrato de ')+name) if not image.endswith('.svg') else '', role=escape(info['role']), links=links_html(person.get('links', {}),prefix,lang), appointments=credentials, name=escape(name), biography=biography, research=related_html(info.get('research_areas',[]),definitions,prefix,lang))
    metadata = f'---\ntitle: {json.dumps(name, ensure_ascii=False)}\npagetitle: {json.dumps(name, ensure_ascii=False)}\ndescription: "Causality Lab: causal inference, biostatistics and epidemiology at the University of Granada."\nlang: "{lang}"\nasset-prefix: "{prefix}"\nalternate-lang: "{"es" if lang == "en" else "en"}"\nalternate-href: "{alternate}{slug}/index.html"\n---\n\n'
    header = (TEMPLATES/f'{lang}-header.html').read_text().replace('__SLUG__',slug)
    footer = (TEMPLATES/f'{lang}-footer.html').read_text()
    target.parent.mkdir(parents=True,exist_ok=True)
    output = metadata+'```{=html}\n'+header+markup+footer+'\n```\n'
    if not target.exists() or target.read_text() != output:
        target.write_text(output)

def update_home(people, lang, definitions):
    path = SITE / ('index.qmd' if lang == 'en' else 'es/index.qmd')
    source = path.read_text()
    prefix = '' if lang == 'en' else '../'
    cards=[]
    for p in people:
        v=p['languages'][lang]
        given, family = p.get('given_name'), p.get('family_name')
        name = (f'<span>{escape(given)}</span> <span>{escape(family)}</span>'
                if given and family else escape(v['name']))
        photo = p.get('home_photo') or p.get('photo') or PLACEHOLDER
        if not (SITE / 'assets' / photo).is_file():
            raise ValueError(f'Homepage image missing: {photo}')
        cards.append(f'<a class="home-person-card" href="team/{attr(p["slug"])}/index.html"><span class="home-person-photo"><img src="{prefix}assets/{attr(photo)}" width="160" height="160" alt="" loading="lazy"></span><div class="home-person-copy"><h3>{name}</h3><p>{escape(v["home_role"])}</p></div></a>')
    pattern = r'(<div class="people-grid people-home-grid">)(.*?)(</div></div><svg class="home-wave")'
    source, count = re.subn(pattern, lambda m: m.group(1)+''.join(cards)+m.group(3), source, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f'Homepage team grid not found in {path}')
    selector_attr, research = research_content(list(definitions), definitions, prefix, '')
    title = 'Research areas' if lang == 'en' else 'Líneas de investigación'
    wave = '<svg class="home-wave" viewBox="0 0 1440 80" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="M0 16 C280 16 420 32 700 48 C980 64 1170 64 1440 64 L1440 80 H0 Z"/></svg>'
    research_section = f'<section class="section research-selector" id="research"{selector_attr}><div class="wrap"><div class="section-heading"><div><h2>{title}</h2></div></div>{research}</div>{wave}</section>'
    source, count = re.subn(r'<section class="section(?: research-selector)?" id="research"[^>]*>.*?</section>', lambda _: research_section, source, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f'Homepage research section not found in {path}')
    if path.read_text() != source:
        path.write_text(source)

def main():
    people = [json.loads(p.read_text()) for p in DATA.glob('*.json')]
    people.sort(key=lambda p: (p.get('order', 9999), p['slug']))
    for lang in ('en','es'):
        definitions = json.loads((SITE/'data'/f'research-{lang}.json').read_text())
        for p in people:
            render_person(p,lang,definitions)
        update_home(people,lang,definitions)

if __name__ == '__main__':
    main()
