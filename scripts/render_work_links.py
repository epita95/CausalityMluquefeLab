#!/usr/bin/env python3
"""Restore alternate resource links recorded in the original site."""
from pathlib import Path
from html import escape, unescape
import re

ROOT = Path(__file__).resolve().parents[1]
BOOK = 'https://migariane.github.io/Causal-Inference-Book/'
GITHUB = 'https://github.com/migariane/Causal-Inference-Book'
DOI = 'https://doi.org/10.5281/zenodo.20677995'
RECORDS = [
    ([BOOK, GITHUB, DOI], BOOK, [('GitHub', GITHUB), ('DOI', DOI)]),
    (['https://arxiv.org/abs/2012.09920', 'https://maluque.netlify.app/publication/cci/'], 'https://arxiv.org/abs/2012.09920', [('Publication', 'https://maluque.netlify.app/publication/cci/')]),
    (['https://github.com/migariane/tmleMulti', 'https://migariane.github.io/tmleMulti'], 'https://migariane.github.io/tmleMulti', [('GitHub', 'https://github.com/migariane/tmleMulti')]),
    (['https://migariane.github.io/ConformalInferenceExplained.html'], 'https://migariane.github.io/ConformalInferenceExplained.html', [('Slides (ES)', 'https://migariane.github.io/ConformalPrediction_Tutorial_ES.html')]),
]

def enrich(block, spanish):
    block = re.sub(r'<div class="work-links"[^>]*>.*?</div>', '', block, flags=re.S)
    hrefs = [unescape(h) for h in re.findall(r'href="([^"]+)"', block)]
    record = next((r for r in RECORDS if any(h.rstrip('/') in {u.rstrip('/') for u in r[0]} for h in hrefs)), None)
    if not record:
        return block
    aliases, primary, extra = record
    if 'class="tool-card"' in block:
        block = re.sub(r'<div class="tool-links">.*?</div>', '', block, flags=re.S)
        block = re.sub(r'<h2>(?!<a\b)(.*?)</h2>', lambda m: f'<h2><a href="{escape(primary, quote=True)}">{m[1]}</a></h2>', block, count=1, flags=re.S)
    # Whole-card links become containers so secondary anchors are valid HTML.
    card = re.fullmatch(r'<a([^>]*class="(?:output-tool|resource-card[^\"]*)"[^>]*)>(.*?)</a>', block, re.S)
    if card:
        attrs, inner = card.groups()
        attrs = re.sub(r'\s+href="[^"]*"', '', attrs)
        inner, count = re.subn(r'<(strong|h2)>(.*?)</\1>', lambda m: f'<{m[1]}><a href="{escape(primary, quote=True)}">{m[2]}</a></{m[1]}>', inner, count=1, flags=re.S)
        if count != 1:
            raise ValueError('Resource title not found')
        block = '<div' + attrs + '>' + inner + '</div>'
    else:
        for alias in aliases:
            pattern = r'(<a\b[^>]*href=")' + re.escape(escape(alias, quote=True)) + r'(")'
            block, count = re.subn(pattern, lambda m: m[1] + escape(primary, quote=True) + m[2], block, count=1)
            if count:
                break
    if 'class="publication-row"' in block:
        block = re.sub(r'(<a class="pub-link" href=")[^"]*(")', lambda m: m[1] + escape(primary, quote=True) + m[2], block)
    existing = {unescape(h).rstrip('/') for h in re.findall(r'href="([^"]+)"', block)}
    links = []
    for label, url in extra:
        if url.rstrip('/') in existing:
            continue
        if spanish:
            label = {'Publication': 'Publicación', 'Slides (ES)': 'Diapositivas (ES)'}.get(label, label)
        links.append(f'<a href="{escape(url, quote=True)}">{label}</a>')
    if links:
        label = 'Enlaces relacionados' if spanish else 'Related links'
        row = f'<div class="work-links" role="group" aria-label="{label}">' + ''.join(links) + '</div>'
        close = block.rfind('</div>') if any(c in block for c in ['class="output-publication"', 'class="publication-row"']) else block.rfind('</')
        block = block[:close] + row + block[close:]
    return block

def main():
    for path in (ROOT / 'site').rglob('*.qmd'):
        if '_site' in path.parts or '.quarto' in path.parts:
            continue
        source = path.read_text()
        spanish = path.relative_to(ROOT / 'site').parts[0] == 'es'
        source = re.sub(r'<article\b[^>]*>.*?</article>', lambda m: enrich(m[0], spanish), source, flags=re.S)
        source = re.sub(r'<a\b[^>]*class="(?:output-tool|resource-card[^\"]*)"[^>]*>.*?</a>', lambda m: enrich(m[0], spanish), source, flags=re.S)
        if path.read_text() != source:
            path.write_text(source)

if __name__ == '__main__':
    main()
