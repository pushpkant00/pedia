# Pedia

A Wikipedia-like encyclopedia: Django backend, rich-text (WYSIWYG) editing,
full-text search, categories, revision history with diffs and rollback,
table of contents, image uploads and red-link "create this page" stubs,
plus editor accounts with roles, an edit-moderation queue and editor settings.

**Repository:** https://github.com/pushpkant00/pedia

## Quick start

```bash
# 1. Create the virtualenv (once) and install dependencies
python3 -m venv --without-pip .venv          # or: python3 -m venv .venv
.venv/bin/python get-pip.py                  # only if pip is missing
.venv/bin/pip install -r requirements.txt

# 2. Prepare the database (once)
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_wiki         # optional demo articles

# 3. Build the JavaScript (required after cloning and after editing src/*.ts)
npm install
npm run build                                # or: npm run watch

# 4. Run
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000/

The first account you register becomes the admin; optional Django admin:

```bash
.venv/bin/python manage.py createsuperuser
```

## Contributing

1. Fork the repo at https://github.com/pushpkant00/pedia and clone your fork.
2. Create a branch: `git checkout -b my-feature`
3. Install dependencies and run the site (see Quick start above).
4. Make your changes, then check them:
   ```bash
   npm install && npm run build   # required once per clone; re-run after touching src/
   .venv/bin/python manage.py check
   .venv/bin/python manage.py test
   ```
5. Commit with a clear message and open a pull request against `main`.

Good first contributions: add or improve articles (bridges, roads, anything),
extend the infobox rows (constructor, owner, materials, design life, cost),
fix bugs, or polish the editor.

## Features

| Feature | Where |
|---|---|
| Article pages with rich text | Toast UI editor (vendored, no CDN), server-side sanitised with `nh3` |
| Create & edit | `/new/`, `/wiki/<slug>/edit/` |
| Search | SQLite FTS5 with highlighted snippets (`articles/search.py`) |
| Table of contents | Auto-generated from headings, collapsible, scrollspy |
| Images / media upload | Editor upload button → `/api/upload/image/` → `/media/uploads/`; click an image in the editor for a red ✕ button that removes it |
| Categories & linking | Category chips, category pages, `[[Page]]` syntax, red links for missing pages |
| History & revisions | `/wiki/<slug>/history/` with diff view and one-click revert |
| Accounts & roles | `/accounts/register/`, admin / editor / viewer roles, blocking |
| Edit moderation | `/review/` pending-edit queue with approve/reject, draft publishing, featured selection |
| Editor settings | `/accounts/settings/` theme, toolbar, autosave, uploads, default summary |

## Project layout

```
wiki/                  project settings, urls, context processor
accounts/              profiles, roles, permissions, settings, moderation UI
articles/              models, views, forms, search, content processing
  content.py           sanitiser, wikilinks, heading IDs, TOC, red links
  search.py            FTS5 search + LIKE fallback
  migrations/          schema + FTS install
templates/wiki/        all page templates
src/                   TypeScript sources (wiki, editor, lightbox, selftest)
static/js/             compiled JS — build output, gitignored (npm run build)
static/                wiki.css, vendored Toast UI assets
media/uploads/         uploaded images
package.json           npm scripts (build/watch) + TypeScript dev dependency
tsconfig.json          tsc configuration (src/ → static/js/)
```

## Notes

- Article URLs are permanent: the slug is generated from the title at creation
  and does not change if the title is later edited.
- Every save records a revision; edit summary, diff and revert are built on that.
- Editors' saves are queued at `/review/` until an admin approves them; admins
  publish immediately.
- The editor loads Toast UI from `static/vendor/`; if it cannot load, a plain
  HTML textarea is shown instead.
- To move to PostgreSQL later, change `DATABASES` in `wiki/settings.py`; the
  search module falls back to `LIKE` automatically if FTS5 is unavailable.
