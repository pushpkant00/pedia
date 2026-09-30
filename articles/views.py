import difflib
import re

from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import escape
from django.utils.text import get_valid_filename
from django.views.decorators.http import require_GET, require_POST

from accounts.permissions import (can_edit, can_review, profile_of,
                                  require_editor, require_reviewer)

from . import content as content_mod
from . import search as search_mod
from .forms import ArticleForm
from .models import Article, Category, Revision, Upload


def _known_slugs():
    return set(Article.objects.values_list('slug', flat=True))


def _editor_prefs(user):
    profile = profile_of(user)
    return profile.editor_prefs if profile else {}


def _may_see(user, article):
    """Published articles are public; drafts are visible to admins and their author."""
    if not article.is_pending:
        return True
    if can_review(user):
        return True
    return article.created_by_id is not None and article.created_by_id == getattr(user, 'pk', None)


def _visible_articles(user):
    qs = Article.objects.all()
    if can_review(user):
        return qs
    if getattr(user, 'is_authenticated', False):
        return qs.filter(Q(is_pending=False) | Q(created_by=user))
    return qs.filter(is_pending=False)


def _visible_revisions(user, queryset=None):
    """Approved history for everyone; your own queued/rejected edits; everything for admins."""
    qs = queryset if queryset is not None else Revision.objects.all()
    if can_review(user):
        return qs
    if getattr(user, 'is_authenticated', False):
        return qs.filter(Q(status=Revision.STATUS_APPROVED) | Q(editor=user))
    return qs.filter(status=Revision.STATUS_APPROVED)


def _may_view_revision(user, revision):
    if revision.status == Revision.STATUS_APPROVED:
        return True
    if can_review(user):
        return True
    return revision.editor_id is not None and revision.editor_id == getattr(user, 'pk', None)


def _publishes_immediately(user, article=None):
    """Admins always publish at once; authors editing their own draft also do."""
    if can_review(user):
        return True
    if article is not None and article.is_pending:
        return article.created_by_id == getattr(user, 'pk', None)
    return False


def _apply_categories(article, form):
    article.categories.set(form.cleaned_data['categories'])
    raw = form.cleaned_data.get('new_categories') or ''
    for name in raw.split(','):
        name = name.strip()
        if not name:
            continue
        category, _ = Category.objects.get_or_create(name__iexact=name,
                                                     defaults={'name': name})
        article.categories.add(category)


def _new_categories(form):
    """Categories a form adds, without touching the article yet (for pending edits)."""
    selected = list(form.cleaned_data['categories'])
    raw = form.cleaned_data.get('new_categories') or ''
    for name in raw.split(','):
        name = name.strip()
        if not name:
            continue
        category, _ = Category.objects.get_or_create(name__iexact=name,
                                                     defaults={'name': name})
        if category not in selected:
            selected.append(category)
    return selected


@require_GET
def home(request):
    visible = _visible_articles(request.user)
    context = {
        'featured': visible.filter(is_featured=True)[:6],
        'recent_articles': visible.order_by('-updated_at')[:8],
        'recent_changes': _visible_revisions(
            request.user, Revision.objects.select_related('article', 'editor'))[:8],
        'article_count': visible.count(),
        'category_count': Category.objects.count(),
        'categories': Category.objects.annotate(n=Count('articles'))[:24],
    }
    return render(request, 'wiki/home.html', context)


def article_detail(request, slug):
    article = Article.objects.filter(slug=slug).first()
    if article is None or not _may_see(request.user, article):
        guessed = ' '.join(part.capitalize() for part in slug.split('-'))
        return render(request, 'wiki/missing.html',
                      {'guessed_title': guessed, 'slug': slug}, status=404)
    body = content_mod.mark_red_links(article.content, _known_slugs())
    pending = _visible_revisions(request.user,
                                 article.revisions.filter(status=Revision.STATUS_PENDING)
                                 .select_related('editor'))[:10]
    context = {
        'article': article,
        'body_html': body,
        'toc': content_mod.build_toc(body),
        'pending_edits': pending,
        'is_author': article.created_by_id == getattr(request.user, 'pk', None),
    }
    return render(request, 'wiki/article_detail.html', context)


@require_editor
def article_create(request):
    initial = {}
    if request.GET.get('title'):
        initial['title'] = request.GET['title'][:255]
    form = ArticleForm(request.POST or None, initial=initial)
    user = request.user
    publish_now = can_review(user)
    if not form.is_bound:
        form.fields['edit_summary'].initial = _editor_prefs(user).get('default_summary', '')
    if request.method == 'POST' and form.is_valid():
        article = Article(
            title=form.cleaned_data['title'],
            summary=form.cleaned_data['summary'],
            content=form.cleaned_data['content'],
            created_by=user,
            is_pending=not publish_now,
        )
        article.save_with_revision(
            summary=form.cleaned_data['edit_summary'] or 'Created article',
            editor=user,
            status='approved' if publish_now else Revision.STATUS_PENDING,
            proposed_title=form.cleaned_data['title'] if not publish_now else None,
            proposed_summary=form.cleaned_data['summary'] if not publish_now else None,
        )
        _apply_categories(article, form)
        if publish_now:
            messages.success(request, f'Article "{article.title}" created.')
        else:
            messages.info(request, f'Article "{article.title}" was saved as a draft and '
                                   f'sent to the review queue.')
        return redirect(article)
    return render(request, 'wiki/article_form.html',
                  {'form': form, 'mode': 'new', 'page_title': 'Create a new article',
                   'editor_prefs': _editor_prefs(user), 'publishes_now': publish_now})


@require_editor
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if not _may_see(request.user, article):
        guessed = ' '.join(part.capitalize() for part in slug.split('-'))
        return render(request, 'wiki/missing.html',
                      {'guessed_title': guessed, 'slug': slug}, status=404)
    user = request.user
    form = ArticleForm(request.POST or None, article=article)
    publish_now = _publishes_immediately(user, article)
    if not form.is_bound:
        form.fields['edit_summary'].initial = _editor_prefs(user).get('default_summary', '')
    if request.method == 'POST' and form.is_valid():
        if publish_now:
            article.title = form.cleaned_data['title']
            article.summary = form.cleaned_data['summary']
            article.content = form.cleaned_data['content']
            article.save_with_revision(
                summary=form.cleaned_data['edit_summary'] or 'Edited article',
                editor=user,
            )
            _apply_categories(article, form)
            messages.success(request, f'Article "{article.title}" saved.')
        else:
            Revision.create_pending(
                article,
                content=form.cleaned_data['content'],
                summary=form.cleaned_data['edit_summary'] or 'Edited article',
                editor=user,
                proposed_title=form.cleaned_data['title'],
                proposed_summary=form.cleaned_data['summary'],
                proposed_categories=_new_categories(form),
            )
            messages.info(request, 'Your edit was saved to the review queue — an admin '
                                   'will publish it soon.')
        return redirect(article)
    return render(request, 'wiki/article_form.html',
                  {'form': form, 'mode': 'edit', 'article': article,
                   'page_title': f'Editing: {article.title}',
                   'editor_prefs': _editor_prefs(user), 'publishes_now': publish_now})


@require_GET
def history(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if not _may_see(request.user, article):
        return render(request, 'wiki/missing.html',
                      {'guessed_title': article.title, 'slug': slug}, status=404)
    revisions = list(_visible_revisions(request.user, article.revisions.all()))
    rows = []
    for index, revision in enumerate(revisions):
        previous = revisions[index + 1] if index + 1 < len(revisions) else None
        rows.append({'revision': revision, 'previous': previous})
    return render(request, 'wiki/history.html',
                  {'article': article, 'rows': rows, 'current': article.content,
                   'pending_edits': [r for r in revisions
                                     if r.status == Revision.STATUS_PENDING]})


@require_GET
def view_revision(request, slug, rev_id):
    article = get_object_or_404(Article, slug=slug)
    revision = get_object_or_404(Revision, pk=rev_id, article=article)
    if not _may_view_revision(request.user, revision):
        messages.error(request, 'That revision is not public yet.')
        return redirect('history', slug=slug)
    body = content_mod.mark_red_links(revision.content, _known_slugs())
    return render(request, 'wiki/article_detail.html', {
        'article': article,
        'body_html': body,
        'toc': content_mod.build_toc(body),
        'revision': revision,
    })


def _resolve_content(request, article, value):
    if value in (None, '', 'current'):
        return article.content, 'current version'
    revision = Revision.objects.filter(pk=value, article=article).first()
    if revision is None or not _may_view_revision(request.user, revision):
        return None, None
    return revision.content, f'revision #{revision.pk}'


def _html_lines(html):
    return re.sub(r'>\s*<', '>\n<', html or '').split('\n')


@require_GET
def revision_diff(request, slug):
    article = get_object_or_404(Article, slug=slug)
    old_html, old_label = _resolve_content(request, article, request.GET.get('old'))
    new_html, new_label = _resolve_content(request, article, request.GET.get('new'))
    if old_html is None or new_html is None:
        return redirect('history', slug=slug)

    diff = list(difflib.unified_diff(_html_lines(old_html), _html_lines(new_html),
                                     fromfile=old_label, tofile=new_label, lineterm=''))
    lines = []
    for line in diff:
        if line.startswith('+++') or line.startswith('---'):
            continue
        if line.startswith('@@'):
            lines.append({'type': 'chunk', 'text': line})
        elif line.startswith('+'):
            lines.append({'type': 'add', 'text': escape(line[1:])})
        elif line.startswith('-'):
            lines.append({'type': 'del', 'text': escape(line[1:])})
        else:
            lines.append({'type': 'ctx', 'text': escape(line[1:])})

    context = {
        'article': article,
        'lines': lines,
        'old_label': old_label,
        'new_label': new_label,
        'empty': not any(l['type'] in ('add', 'del') for l in lines),
    }
    return render(request, 'wiki/diff.html', context)


@require_POST
@require_editor
def revert(request, slug, rev_id):
    article = get_object_or_404(Article, slug=slug)
    revision = get_object_or_404(Revision, pk=rev_id, article=article)
    if _publishes_immediately(request.user, article):
        article.content = revision.content
        article.save_with_revision(summary=f'Reverted to revision #{revision.pk}',
                                   editor=request.user)
        messages.success(request, f'Reverted to revision #{revision.pk}.')
    else:
        Revision.create_pending(
            article,
            content=revision.content,
            summary=f'Revert to revision #{revision.pk}',
            editor=request.user,
            proposed_title=article.title,
            proposed_summary=article.summary,
        )
        messages.info(request, f'Revert to revision #{revision.pk} queued for review.')
    return redirect('history', slug=slug)


@require_GET
def search(request):
    query = (request.GET.get('q') or '').strip()
    results = search_mod.search_articles(query) if query else []
    results = [r for r in results if _may_see(request.user, r['article'])]
    if query and not results:
        for article in _visible_articles(request.user).filter(title__icontains=query)[:20]:
            snippet = article.summary or (article.plain_text[:160] + '…')
            results.append({'article': article, 'snippet': escape(snippet)})
    context = {
        'query': query,
        'results': results,
        'count': len(results),
    }
    return render(request, 'wiki/search.html', context)


@require_GET
def recent_changes(request):
    revisions = _visible_revisions(
        request.user, Revision.objects.select_related('article', 'editor'))[:80]
    return render(request, 'wiki/recent.html', {'revisions': revisions})


@require_GET
def random_article(request):
    ids = list(_visible_articles(request.user).values_list('id', flat=True))
    if not ids:
        messages.info(request, 'No articles yet — be the first to write one.')
        return redirect('home')
    import random
    article_id = random.choice(ids)
    return redirect('article_detail', slug=Article.objects.get(pk=article_id).slug)


@require_GET
def category_index(request):
    categories = Category.objects.annotate(n=Count('articles')).order_by('name')
    return render(request, 'wiki/categories.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = _visible_articles(request.user).filter(categories=category).order_by('title')
    return render(request, 'wiki/category.html',
                  {'category': category, 'articles': articles})


@require_editor
def upload_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)
    profile = profile_of(request.user)
    if profile is None or not profile.setting('uploads'):
        return JsonResponse({'error': 'Image uploads are switched off in your editor '
                                      'settings.'}, status=403)
    upload_file = request.FILES.get('file')
    if upload_file is None:
        return JsonResponse({'error': 'No file provided.'}, status=400)
    if upload_file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'Image exceeds the 10 MB limit.'}, status=400)

    from PIL import Image, UnidentifiedImageError
    try:
        image = Image.open(upload_file)
        image_format = (image.format or '').upper()
        image.verify()
    except (UnidentifiedImageError, OSError):
        return JsonResponse({'error': 'File is not a valid image.'}, status=400)

    allowed = {'PNG', 'JPEG', 'GIF', 'WEBP', 'BMP'}
    if image_format not in allowed:
        return JsonResponse({'error': 'Unsupported image format.'}, status=400)

    original_name = get_valid_filename(upload_file.name or 'image')
    upload = Upload.objects.create(original_name=original_name, file=upload_file)
    return JsonResponse({'url': upload.file.url, 'alt': original_name})


# --- Review queue (admins) -------------------------------------------------


@require_GET
@require_reviewer
def review_queue(request):
    pending_revisions = (Revision.objects
                         .filter(status=Revision.STATUS_PENDING)
                         .select_related('article', 'editor')
                         .order_by('-created_at'))
    pending_articles = (Article.objects
                        .filter(is_pending=True)
                        .select_related('created_by')
                        .order_by('-created_at'))
    all_articles = Article.objects.order_by('title')
    context = {
        'pending_revisions': pending_revisions,
        'pending_articles': pending_articles,
        'all_articles': all_articles,
        'queue_empty': not pending_revisions and not pending_articles,
    }
    return render(request, 'wiki/review.html', context)


@require_POST
@require_reviewer
def review_revision(request, rev_id):
    revision = get_object_or_404(Revision, pk=rev_id,
                                 status=Revision.STATUS_PENDING)
    action = request.POST.get('action')
    article = revision.article
    back = request.POST.get('next') or 'review_queue'

    if action == 'approve':
        if revision.proposed_title:
            article.title = revision.proposed_title
        if revision.proposed_summary:
            article.summary = revision.proposed_summary
        article.content = revision.content
        article.is_pending = False
        article.save()
        categories = list(revision.proposed_categories.all())
        if categories:
            article.categories.set(categories)
        revision.status = Revision.STATUS_APPROVED
        revision.reviewed_by = request.user
        revision.reviewed_at = timezone.now()
        revision.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
        who = revision.editor.username if revision.editor_id else 'an editor'
        messages.success(request, f'Approved edit by {who} on "{article.title}".')
    elif action == 'reject':
        revision.status = Revision.STATUS_REJECTED
        revision.reviewed_by = request.user
        revision.reviewed_at = timezone.now()
        revision.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
        messages.info(request, f'Rejected the pending edit on "{article.title}".')
    else:
        messages.error(request, 'Unknown review action.')
    if back and back.startswith('/') and not back.startswith('//'):
        return redirect(back)
    return redirect('review_queue')


@require_POST
@require_reviewer
def review_draft(request, article_id):
    article = get_object_or_404(Article, pk=article_id, is_pending=True)
    action = request.POST.get('action')
    if action == 'approve':
        article.is_pending = False
        article.save(update_fields=['is_pending'])
        article.revisions.filter(status=Revision.STATUS_PENDING).update(
            status=Revision.STATUS_APPROVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        messages.success(request, f'Published "{article.title}".')
    elif action == 'reject':
        title = article.title
        article.delete()
        messages.info(request, f'Rejected the draft "{title}".')
    else:
        messages.error(request, 'Unknown review action.')
    return redirect('review_queue')


@require_POST
@require_reviewer
def featured_toggle(request, slug):
    article = get_object_or_404(Article, slug=slug)
    article.is_featured = not article.is_featured
    article.save(update_fields=['is_featured'])
    if article.is_featured:
        messages.success(request, f'"{article.title}" is now featured on the main page.')
    else:
        messages.info(request, f'"{article.title}" removed from featured articles.')
    back = request.POST.get('next')
    return redirect(back) if back and back.startswith('/') else redirect('review_queue')
