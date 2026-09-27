# Pedia

A Wikipedia-like encyclopedia: Django backend, rich-text (WYSIWYG) editing,
full-text search, categories, revision history with diffs and rollback,
table of contents, image uploads and red-link "create this page" stubs.

## Quick start

```bash
# 1. Create the virtualenv (once) and install dependencies
python3 -m venv --without-pip .venv          # or: python3 -m venv .venv
.venv/bin/python get-pip.py                  # only if pip is missing
.venv/bin/pip install -r requirements.txt

# 2. Prepare the database (once)
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_wiki         # optional demo articles

# 3. Run
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000/

Optional admin account (for `/admin/` and featured-article flags):

```bash
.venv/bin/python manage.py createsuperuser
```

## Features

| Feature | Where |
|---|---|
| Article pages with rich text | Toast UI editor (CDN), server-side sanitised with `nh3` |
| Create & edit | `/new/`, `/wiki/<slug>/edit/` |
| Search | SQLite FTS5 with highlighted snippets (`articles/search.py`) |
| Table of contents | Auto-generated from headings, collapsible, scrollspy |
| Images / media upload | Editor upload button → `/api/upload/image/` → `/media/uploads/` |
| Categories & linking | Category chips, category pages, `[[Page]]` syntax, red links for missing pages |
| History & revisions | `/wiki/<slug>/history/` with diff view and one-click revert |

## Project layout

```
wiki/                  project settings, urls, context processor
articles/              models, views, forms, search, content processing
  content.py           sanitiser, wikilinks, heading IDs, TOC, red links
  search.py            FTS5 search + LIKE fallback
  migrations/          schema + FTS install
templates/wiki/        all page templates
static/                wiki.css, editor.js, wiki.js
media/uploads/         uploaded images
```

## Notes

- Article URLs are permanent: the slug is generated from the title at creation
  and does not change if the title is later edited.
- Every save records a revision; edit summary, diff and revert are built on that.
- The editor requires internet access (Toast UI CDN); if it cannot load, a plain
  HTML textarea is shown instead.
- To move to PostgreSQL later, change `DATABASES` in `wiki/settings.py`; the
  search module falls back to `LIKE` automatically if FTS5 is unavailable.

## Deferred (planned next)

- User accounts, edit attribution and permissions (Django auth is already wired in)
- Talk pages, watchlists, page moves
