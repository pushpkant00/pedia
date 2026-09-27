from django import forms
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import Article, Category


class ArticleForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'input-title',
            'placeholder': 'Article title',
            'autocomplete': 'off',
        }),
    )
    summary = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-summary',
            'placeholder': 'One-line summary (shown in search results)',
        }),
    )
    content = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_content'}),
    )
    edit_summary = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-summary',
            'placeholder': 'Brief description of your change',
        }),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'category-checks'}),
    )
    new_categories = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-summary',
            'placeholder': 'New categories, comma separated',
        }),
    )

    def __init__(self, *args, article=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.article = article
        if article is not None and not self.is_bound:
            self.fields['title'].initial = article.title
            self.fields['summary'].initial = article.summary
            self.fields['content'].initial = article.content
            self.fields['categories'].initial = article.categories.all()

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if not title:
            raise forms.ValidationError('A title is required.')
        qs = Article.objects.filter(title__iexact=title)
        if self.article is not None:
            qs = qs.exclude(pk=self.article.pk)
        if qs.exists():
            existing = qs.first()
            raise forms.ValidationError(mark_safe(
                f'An article named "{escape(existing.title)}" already exists. '
                f'<a href="{existing.get_absolute_url()}">Open it instead</a>.'
            ))
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content') or ''
        if not content.strip():
            raise forms.ValidationError('The article body cannot be empty.')
        return content
