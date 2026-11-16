#!/usr/bin/env python3
"""Check generated pages, local references, fragments and language pairs."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site/_site'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.headings, self.images = [], set(), [], []
        self.language = self.opposite = None
        self.footer = self.main = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag in ('a', 'link') and attrs.get('href'):
            self.refs.append(attrs['href'])
        if tag in ('img', 'script', 'source') and attrs.get('src'):
            self.refs.append(attrs['src'])
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'h1' or (attrs.get('role') == 'heading' and attrs.get('aria-level') == '1'):
            self.headings.append(attrs)
        if tag == 'html':
            self.language = attrs.get('lang')
        if tag == 'a' and 'language-option' in attrs.get('class', '').split():
            self.opposite = attrs.get('href')
        if tag == 'footer':
            self.footer += 1
        if tag == 'main':
            self.main += 1


def main():
    parsed = {}
    errors, checked = [], 0
    for file in SITE.rglob('index.html'):
        parser = Page()
        parser.feed(file.read_text())
        parsed[file.resolve()] = parser
    expected = 2 * (5 + len(json.loads((ROOT/'site/data/content.json').read_text())['people']))
    if len(parsed) != expected:
        errors.append(f'Expected {expected} pages; found {len(parsed)}')
    for file, page in parsed.items():
        relative = file.relative_to(SITE.resolve()).as_posix()
        if len(page.headings) != 1 or page.main != 1 or page.footer != 1:
            errors.append(f'{relative}: missing or duplicate main, footer or h1')
        if page.language != ('es' if relative.startswith('es/') else 'en'):
            errors.append(f'{relative}: incorrect document language')
        if any('alt' not in image for image in page.images):
            errors.append(f'{relative}: image without alt')
        for reference in page.refs:
            url = urlsplit(reference)
            if url.scheme or url.netloc:
                continue
            checked += 1
            target = (file.parent / unquote(url.path)).resolve() if url.path else file
            if not target.exists():
                errors.append(f'{relative}: missing {reference}')
            elif url.fragment and target in parsed and unquote(url.fragment) not in parsed[target].ids:
                errors.append(f'{relative}: missing fragment {reference}')
        expected_other = relative.removeprefix('es/') if relative.startswith('es/') else 'es/'+relative
        if not page.opposite or (file.parent/page.opposite).resolve() != (SITE/expected_other).resolve():
            errors.append(f'{relative}: language switch loses page context')
    result = {'pages': len(parsed), 'local_references_checked': checked, 'errors': errors, 'scope': 'Generated local files, fragments, language pairs, headings, landmarks and image alt attributes; external links not fetched.'}
    (ROOT/'preview').mkdir(exist_ok=True)
    (ROOT/'preview/structure-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
