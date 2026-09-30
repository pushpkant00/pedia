from django.conf import settings
from django.db import models

EDITOR_SETTING_DEFAULTS = {
    'default_summary': '',
    'initial_mode': 'wysiwyg',
    'toolbar': 'full',
    'theme': 'light',
    'autosave': True,
    'autosave_interval': 30,
    'uploads': True,
}


class Profile(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_EDITOR = 'editor'
    ROLE_VIEWER = 'viewer'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin — publishes immediately and reviews edits'),
        (ROLE_EDITOR, 'Editor — edits are queued for review'),
        (ROLE_VIEWER, 'Viewer — read-only'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_EDITOR)
    is_blocked = models.BooleanField(default=False, help_text='Blocked editors cannot edit or review.')
    editor_settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display().split(" —")[0]})'

    @property
    def display_role(self):
        return self.get_role_display().split(' —')[0].strip()

    @property
    def editor_prefs(self):
        merged = dict(EDITOR_SETTING_DEFAULTS)
        merged.update(self.editor_settings or {})
        return merged

    def setting(self, name):
        return self.editor_prefs.get(name, EDITOR_SETTING_DEFAULTS.get(name))

    @property
    def can_edit(self):
        return (not self.is_blocked) and self.role in (self.ROLE_ADMIN, self.ROLE_EDITOR)

    @property
    def can_review(self):
        return (not self.is_blocked) and self.role == self.ROLE_ADMIN
