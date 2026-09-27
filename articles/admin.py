from django.contrib import admin

from .models import Article, Category, Revision, Upload


class RevisionInline(admin.TabularInline):
    model = Revision
    extra = 0
    readonly_fields = ('content', 'summary', 'created_at')
    can_delete = False
    show_change_link = True


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at', 'is_featured')
    list_filter = ('is_featured', 'categories')
    search_fields = ('title', 'content')
    filter_horizontal = ('categories',)
    inlines = [RevisionInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('article', 'summary', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('article', 'content', 'summary', 'created_at')


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'created_at')
    readonly_fields = ('file', 'original_name', 'created_at')
