import re
import sqlite3

from django.db import connection
from django.utils.html import escape

MARK_OPEN = '\x02'
MARK_CLOSE = '\x03'

TOKEN_RE = re.compile(r'[A-Za-z0-9_]+')

DDL = [
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS article_fts USING fts5(
        article_id UNINDEXED,
        title,
        body
    );
    """,
    """
    CREATE TRIGGER IF NOT EXISTS article_fts_ai AFTER INSERT ON articles_article BEGIN
        INSERT INTO article_fts(article_id, title, body)
        VALUES (new.id, new.title, new.text_content);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS article_fts_au AFTER UPDATE ON articles_article BEGIN
        DELETE FROM article_fts WHERE article_id = old.id;
        INSERT INTO article_fts(article_id, title, body)
        VALUES (new.id, new.title, new.text_content);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS article_fts_ad AFTER DELETE ON articles_article BEGIN
        DELETE FROM article_fts WHERE article_id = old.id;
    END;
    """,
]


def install_fts(connection_obj=None):
    conn = connection_obj or connection
    for stmt in DDL:
        conn.cursor().execute(stmt)


def ensure_fts():
    try:
        install_fts()
    except sqlite3.Error:
        pass


def build_match_query(query):
    tokens = TOKEN_RE.findall(query)
    if not tokens:
        return ''
    parts = [f'"{t}"' for t in tokens[:-1]]
    parts.append(f'"{tokens[-1]}"*')
    return ' '.join(parts)


def _format_snippet(raw):
    html = escape(raw.strip())
    html = html.replace(MARK_OPEN, '<mark>').replace(MARK_CLOSE, '</mark>')
    return html


def _fts_search(query):
    match = build_match_query(query)
    if not match:
        return []
    sql = """
        SELECT a.id, a.title, a.slug, a.summary, a.updated_at,
               snippet(article_fts, 2, %s, %s, '…', 14) AS snip,
               bm25(article_fts) AS rank
        FROM article_fts
        JOIN articles_article a ON a.id = article_fts.article_id
        WHERE article_fts MATCH %s
        ORDER BY rank
        LIMIT 30
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [MARK_OPEN, MARK_CLOSE, match])
        rows = cursor.fetchall()

    from .models import Article
    results = []
    for row in rows:
        article = Article.objects.filter(pk=row[0]).first()
        if not article:
            continue
        results.append({'article': article, 'snippet': _format_snippet(row[5] or article.summary)})
    return results


def _like_search(query):
    from .models import Article
    tokens = TOKEN_RE.findall(query)
    if not tokens:
        return []
    qs = Article.objects.all()
    for token in tokens:
        qs = qs.filter(text_content__icontains=token)
    results = []
    for article in qs[:30]:
        text = article.plain_text
        pos = text.lower().find(tokens[0].lower())
        if pos >= 0:
            start = max(0, pos - 60)
            raw = ('…' if start else '') + text[start:start + 160] + '…'
        else:
            raw = text[:160] + ('…' if len(text) > 160 else '')
        results.append({'article': article, 'snippet': escape(raw)})
    return results


def search_articles(query):
    query = (query or '').strip()
    if not query:
        return []
    try:
        ensure_fts()
        return _fts_search(query)
    except sqlite3.Error:
        return _like_search(query)
    except Exception:
        return _like_search(query)
