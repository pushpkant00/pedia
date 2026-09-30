from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from . import content as content_mod


def make_unique_slug(model, title, exclude_pk=None):
    base = slugify(title) or 'untitled'
    slug = base
    counter = 2
    qs = model.objects.all()
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=slug).exists():
        slug = f'{base}-{counter}'
        counter += 1
    return slug


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_unique_slug(Category, self.name, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])


class Article(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField(blank=True, help_text='Article body (HTML).')
    text_content = models.TextField(blank=True, editable=False)
    summary = models.CharField(max_length=500, blank=True,
                               help_text='One-line description shown in search and listings.')
    categories = models.ManyToManyField(Category, blank=True, related_name='articles')
    is_featured = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False,
                                     help_text='Draft awaiting review by an admin.')
    created_by = models.ForeignKey('auth.User', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='created_articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_unique_slug(Article, self.title, exclude_pk=self.pk)
        self.content = content_mod.process(self.content)
        self.text_content = content_mod.strip_to_text(self.content)
        super().save(*args, **kwargs)

    def save_with_revision(self, summary='', editor=None, status='approved',
                           proposed_title=None, proposed_summary=None):
        """Persist the article and record a revision.

        Pending revisions store the *proposed* title/summary alongside their content so
        an admin can approve the whole edit later; the article itself is untouched until
        then.
        """
        self.save()
        Revision.objects.create(
            article=self, content=self.content,
            summary=(summary or '')[:300],
            editor=editor if getattr(editor, 'is_authenticated', False) else None,
            status=status,
            proposed_title=(proposed_title or '')[:255],
            proposed_summary=(proposed_summary or '')[:500],
        )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.slug])

    @property
    def toc(self):
        return content_mod.build_toc(self.content)

    @property
    def plain_text(self):
        return content_mod.strip_to_text(self.content)


class Revision(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='revisions')
    content = models.TextField()
    summary = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    editor = models.ForeignKey('auth.User', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='revisions')
    reviewed_by = models.ForeignKey('auth.User', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='reviews_done')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    proposed_title = models.CharField(max_length=255, blank=True,
                                      help_text='Title requested by a pending edit.')
    proposed_summary = models.CharField(max_length=500, blank=True,
                                        help_text='Summary requested by a pending edit.')
    proposed_categories = models.ManyToManyField(Category, blank=True,
                                                  related_name='pending_revisions',
                                                  help_text='Categories requested by a pending edit.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.article.title} @ {self.created_at:%Y-%m-%d %H:%M}'

    @property
    def number(self):
        return self.pk

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @classmethod
    def create_pending(cls, article, content, summary='', editor=None,
                       proposed_title=None, proposed_summary=None,
                       proposed_categories=None):
        """Queue an edit without touching the live article."""
        revision = cls.objects.create(
            article=article,
            content=content_mod.process(content),
            summary=(summary or '')[:300],
            status=cls.STATUS_PENDING,
            editor=editor if getattr(editor, 'is_authenticated', False) else None,
            proposed_title=(proposed_title or '')[:255],
            proposed_summary=(proposed_summary or '')[:500],
        )
        if proposed_categories is not None:
            revision.proposed_categories.set(proposed_categories)
        return revision


class Upload(models.Model):
    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.original_name

    @property
    def url(self):
        return self.file.url
