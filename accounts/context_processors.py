from .permissions import profile_of


def account(request):
    """Role flags for templates plus the review-queue badge count."""
    user = getattr(request, 'user', None)
    signed_in = bool(user is not None and getattr(user, 'is_authenticated', False))
    profile = profile_of(user) if signed_in else None

    if not signed_in:
        role = 'Visitor'
    elif profile is None:
        role = 'Editor'
    elif profile.is_blocked:
        role = 'Suspended'
    else:
        role = profile.display_role

    is_admin = bool(profile and profile.can_review)
    can_edit = bool(profile and profile.can_edit)

    pending = 0
    if is_admin:
        from articles.models import Article, Revision
        pending = (Revision.objects.filter(status='pending').count()
                   + Article.objects.filter(is_pending=True).count())

    return {
        'viewer_role': role,
        'can_edit': can_edit,
        'is_admin': is_admin,
        'is_signed_in': signed_in,
        'is_blocked': bool(profile and profile.is_blocked),
        'pending_review_count': pending,
        'editor_prefs': profile.editor_prefs if profile else {},
    }
