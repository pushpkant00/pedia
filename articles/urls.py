from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.article_create, name='article_create'),
    path('search/', views.search, name='search'),
    path('recent/', views.recent_changes, name='recent_changes'),
    path('random/', views.random_article, name='random_article'),
    path('categories/', views.category_index, name='category_index'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('wiki/<slug:slug>/edit/', views.article_edit, name='article_edit'),
    path('wiki/<slug:slug>/history/', views.history, name='history'),
    path('wiki/<slug:slug>/history/diff/', views.revision_diff, name='revision_diff'),
    path('wiki/<slug:slug>/history/<int:rev_id>/', views.view_revision, name='view_revision'),
    path('wiki/<slug:slug>/history/<int:rev_id>/revert/', views.revert, name='revert'),
    path('wiki/<slug:slug>/feature/', views.featured_toggle, name='featured_toggle'),
    path('wiki/<slug:slug>/', views.article_detail, name='article_detail'),
    path('review/', views.review_queue, name='review_queue'),
    path('review/revision/<int:rev_id>/', views.review_revision, name='review_revision'),
    path('review/draft/<int:article_id>/', views.review_draft, name='review_draft'),
    path('api/upload/image/', views.upload_image, name='upload_image'),
]
