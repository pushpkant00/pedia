from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import EditorSettingsForm, RegisterForm, RoleForm
from .models import Profile
from .permissions import can_review, profile_of


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        profile = profile_of(user)
        if profile and profile.role == Profile.ROLE_ADMIN:
            messages.success(request, f'Welcome, {user.username} — the first account is the '
                                      f'wiki admin. You publish edits immediately and review '
                                      f'everyone else’s.')
        else:
            messages.success(request, f'Welcome, {user.username}. Your account is an editor: '
                                      f'submitted edits go to the review queue.')
        return redirect('home')
    return render(request, 'wiki/register.html', {'form': form})


@require_POST
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('home')


@login_required
def editor_settings(request):
    profile = profile_of(request.user)
    form = EditorSettingsForm(request.POST or None, profile=profile)
    if request.method == 'POST' and form.is_valid():
        profile.editor_settings = form.cleaned_settings()
        profile.save(update_fields=['editor_settings'])
        messages.success(request, 'Editor settings saved.')
        return redirect('editor_settings')
    return render(request, 'wiki/settings.html', {'form': form, 'profile': profile})


def people(request):
    if not can_review(request.user):
        messages.error(request, 'Managing editors is limited to admins.')
        return redirect('home')
    form = RoleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        target = get_object_or_404(User, pk=form.cleaned_data['user_id'])
        target_profile = profile_of(target)
        if target_profile is None:
            target_profile = Profile.objects.create(user=target, role=Profile.ROLE_EDITOR)
        new_role = form.cleaned_data['role']
        if (target_profile.role == Profile.ROLE_ADMIN and new_role != Profile.ROLE_ADMIN
                and Profile.objects.filter(role=Profile.ROLE_ADMIN, is_blocked=False).count() <= 1):
            messages.error(request, 'This is the last active admin — promote someone else first.')
            return redirect('people')
        target_profile.role = new_role
        target_profile.is_blocked = bool(form.cleaned_data['is_blocked'])
        target_profile.save(update_fields=['role', 'is_blocked'])
        target.is_staff = (new_role == Profile.ROLE_ADMIN)
        target.save(update_fields=['is_staff'])
        if target == request.user:
            messages.warning(request, 'You changed your own role.')
        else:
            messages.success(request, f'{target.username} is now '
                                      f'{target_profile.display_role.lower()}'
                                      f'{" and blocked" if target_profile.is_blocked else ""}.')
        return redirect('people')

    from articles.models import Revision

    rows = []
    for profile in Profile.objects.select_related('user'):
        rows.append({
            'profile': profile,
            'edits': Revision.objects.filter(editor=profile.user, status='approved').count(),
        })
    return render(request, 'wiki/people.html',
                  {'rows': rows, 'form': form, 'roles': Profile.ROLE_CHOICES})
