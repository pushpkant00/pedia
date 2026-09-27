import difflib
import re

from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import escape
from django.utils.text import get_valid_filename
from django.views.decorators.http import require_GET, require_POST

from . import content as content_mod
from . import search as search_mod
from .forms import ArticleForm
from .models import Article, Category, Revision, Upload


def _known_slugs():
    return set(Article.objects.values_list('slug', flat=True))


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


@require_GET
def home(request):
    context = {
        'featured': Article.objects.filter(is_featured=True)[:6],
        'recent_articles': Article.objects.order_by('-updated_at')[:8],
        'recent_changes': Revision.objects.select_related('article')[:8],
        'article_count': Article.objects.count(),
        'category_count': Category.objects.count(),
        'categories': Category.objects.annotate(n=Count('articles'))[:24],
    }
    return render(request, 'wiki/home.html', context)


def article_detail(request, slug):
    article = Article.objects.filter(slug=slug).first()
    if article is None:
        guessed = ' '.join(part.capitalize() for part in slug.split('-'))
        return render(request, 'wiki/missing.html',
                      {'guessed_title': guessed, 'slug': slug}, status=404)
    body = content_mod.mark_red_links(article.content, _known_slugs())
    context = {
        'article': article,
        'body_html': body,
        'toc': content_mod.build_toc(body),
    }
    return render(request, 'wiki/article_detail.html', context)


def article_create(request):
    initial = {}
    if request.GET.get('title'):
        initial['title'] = request.GET['title'][:255]
    form = ArticleForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        article = Article(
            title=form.cleaned_data['title'],
            summary=form.cleaned_data['summary'],
            content=form.cleaned_data['content'],
        )
        article.save_with_revision(summary=form.cleaned_data['edit_summary'] or 'Created article')
        _apply_categories(article, form)
        messages.success(request, f'Article "{article.title}" created.')
        return redirect(article)
    return render(request, 'wiki/article_form.html',
                  {'form': form, 'mode': 'new', 'page_title': 'Create a new article'})


def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)
    form = ArticleForm(request.POST or None, article=article)
    if request.method == 'POST' and form.is_valid():
        article.title = form.cleaned_data['title']
        article.summary = form.cleaned_data['summary']
        article.content = form.cleaned_data['content']
        article.save_with_revision(summary=form.cleaned_data['edit_summary'] or 'Edited article')
        _apply_categories(article, form)
        messages.success(request, f'Article "{article.title}" saved.')
        return redirect(article)
    return render(request, 'wiki/article_form.html',
                  {'form': form, 'mode': 'edit', 'article': article,
                   'page_title': f'Editing: {article.title}'})


@require_GET
def history(request, slug):
    article = get_object_or_404(Article, slug=slug)
    revisions = list(article.revisions.all())
    rows = []
    for index, revision in enumerate(revisions):
        previous = revisions[index + 1] if index + 1 < len(revisions) else None
        rows.append({'revision': revision, 'previous': previous})
    return render(request, 'wiki/history.html',
                  {'article': article, 'rows': rows, 'current': article.content})


@require_GET
def view_revision(request, slug, rev_id):
    article = get_object_or_404(Article, slug=slug)
    revision = get_object_or_404(Revision, pk=rev_id, article=article)
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
    if revision is None:
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
def revert(request, slug, rev_id):
    article = get_object_or_404(Article, slug=slug)
    revision = get_object_or_404(Revision, pk=rev_id, article=article)
    article.content = revision.content
    article.save_with_revision(summary=f'Reverted to revision #{revision.pk}')
    messages.success(request, f'Reverted to revision #{revision.pk}.')
    return redirect('history', slug=slug)


@require_GET
def search(request):
    query = (request.GET.get('q') or '').strip()
    results = search_mod.search_articles(query) if query else []
    if query and not results:
        for article in Article.objects.filter(title__icontains=query)[:20]:
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
    revisions = Revision.objects.select_related('article')[:80]
    return render(request, 'wiki/recent.html', {'revisions': revisions})


@require_GET
def random_article(request):
    ids = list(Article.objects.values_list('id', flat=True))
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
    articles = category.articles.order_by('title')
    return render(request, 'wiki/category.html',
                  {'category': category, 'articles': articles})


@require_POST
def upload_image(request):
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
