from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .models import Profile


def profile_of(user):
    if not getattr(user, 'is_authenticated', False):
        return None
    return getattr(user, 'profile', None)


def role_of(user):
    profile = profile_of(user)
    return profile.role if profile else None


def can_edit(user):
    profile = profile_of(user)
    return bool(profile and profile.can_edit)


def can_review(user):
    profile = profile_of(user)
    return bool(profile and profile.can_review)


def _blocked(request):
    profile = profile_of(request.user)
    return bool(profile and profile.is_blocked)


def require_editor(view):
    """Anonymous users go to the login page; viewers and blocked editors get a message."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if _blocked(request):
            messages.error(request, 'Your account has been suspended and cannot edit.')
            return redirect('home')
        if not can_edit(request.user):
            messages.error(request, 'Your account has read-only access — ask an admin to '
                                    'upgrade your role to edit.')
            return redirect('home')
        return view(request, *args, **kwargs)
    return wrapper


def require_reviewer(view):
    """Admins only (blocked admins lose access)."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if _blocked(request) or not can_review(request.user):
            messages.error(request, 'The review queue is limited to admins.')
            return redirect('home')
        return view(request, *args, **kwargs)
    return wrapper
