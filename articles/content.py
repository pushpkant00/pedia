import re
from html import escape
from html.parser import HTMLParser

import nh3
from django.utils.text import slugify

ALLOWED_TAGS = {
    'p', 'br', 'hr', 'div', 'span',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u', 's', 'strike', 'del', 'ins',
    'sub', 'sup', 'small', 'mark', 'kbd', 'abbr', 'cite',
    'blockquote', 'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'a', 'img', 'code', 'pre', 'figure', 'figcaption',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption',
    'input',
}

ALLOWED_ATTRIBUTES = {
    '*': {'class', 'id', 'title'},
    'a': {'href', 'title'},
    'img': {'src', 'alt', 'title', 'width', 'height'},
    'ol': {'start'},
    'code': {'class'},
    'pre': {'class'},
    'td': {'colspan', 'rowspan'},
    'th': {'colspan', 'rowspan', 'scope'},
    'input': {'type', 'disabled', 'checked'},
}

HEADING_RE = re.compile(r'<h([1-6])([^>]*)>(.*?)</h\1>', re.S | re.I)
WIKILINK_RE = re.compile(r'\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]')
ANCHOR_RE = re.compile(r'\bid="([^"]+)"')


def expand_wikilinks(html):
    def repl(match):
        target = match.group(1).strip()
        label = (match.group(2) or match.group(1)).strip()
        slug = slugify(target) or 'article'
        return f'<a href="/wiki/{slug}/">{escape(label)}</a>'

    return WIKILINK_RE.sub(repl, html)


def clean(html):
    if not html:
        return ''
    return nh3.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)


def ensure_heading_ids(html):
    used = set()

    for match in HEADING_RE.finditer(html):
        id_match = ANCHOR_RE.search(match.group(2))
        if id_match:
            used.add(id_match.group(1))

    def repl(match):
        level, attrs, inner = match.group(1), match.group(2), match.group(3)
        if ANCHOR_RE.search(attrs):
            return match.group(0)
        text = re.sub(r'<[^>]+>', '', inner)
        base = slugify(text) or f'section-{len(used) + 1}'
        candidate, counter = base, 2
        while candidate in used:
            candidate = f'{base}-{counter}'
            counter += 1
        used.add(candidate)
        return f'<h{level}{attrs} id="{candidate}">{inner}</h{level}>'

    return HEADING_RE.sub(repl, html)


def process(raw_html):
    html = expand_wikilinks(raw_html or '')
    html = clean(html)
    html = ensure_heading_ids(html)
    return html


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def strip_to_text(html):
    parser = _TextExtractor()
    parser.feed(html or '')
    text = ' '.join(parser.parts)
    return re.sub(r'\s+', ' ', text).strip()


def build_toc(html, max_level=4):
    entries = []
    for match in HEADING_RE.finditer(html or ''):
        level = int(match.group(1))
        if level > max_level:
            continue
        id_match = ANCHOR_RE.search(match.group(2))
        text = re.sub(r'<[^>]+>', '', match.group(3))
        text = re.sub(r'\s+', ' ', text).strip()
        if not text:
            continue
        entries.append({
            'level': level,
            'id': id_match.group(1) if id_match else '',
            'text': text,
        })
    return entries


WIKI_HREF_RE = re.compile(r'<a\s+([^>]+)>')


def mark_red_links(html, known_slugs):
    def repl(match):
        attrs = match.group(1)
        href_match = re.search(r'href="([^"]*)"', attrs)
        if not href_match:
            return match.group(0)
        slug_match = re.match(r'/wiki/([A-Za-z0-9_-]+)', href_match.group(1))
        if not slug_match or slug_match.group(1) in known_slugs:
            return match.group(0)
        class_match = re.search(r'class="([^"]*)"', attrs)
        if class_match:
            classes = class_match.group(1).split()
            if 'new' not in classes:
                classes.append('new')
            attrs = attrs[:class_match.start(1)] + ' '.join(classes) + attrs[class_match.end(1):]
        else:
            attrs = f'class="new" {attrs}'
        return f'<a {attrs}>'

    return WIKI_HREF_RE.sub(repl, html or '')


def extract_linked_slugs(html):
    slugs = set()
    for match in re.finditer(r'href="/wiki/([A-Za-z0-9_-]+)', html or ''):
        slugs.add(match.group(1))
    return slugs
