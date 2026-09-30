from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='wiki/login.html',
                                     redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.editor_settings, name='editor_settings'),
    path('people/', views.people, name='people'),
]
