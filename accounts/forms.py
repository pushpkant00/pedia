from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import EDITOR_SETTING_DEFAULTS, Profile


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input-summary',
                                               'placeholder': 'Username',
                                               'autocomplete': 'username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('password1', 'password2'):
            self.fields[name].widget.attrs.update({'class': 'input-summary',
                                                   'autocomplete': 'new-password'})


class EditorSettingsForm(forms.Form):
    MODE_CHOICES = [('wysiwyg', 'Visual (WYSIWYG)'), ('markdown', 'Markdown / source')]
    TOOLBAR_CHOICES = [('full', 'Full toolbar'), ('compact', 'Compact toolbar')]
    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark')]
    INTERVAL_CHOICES = [(10, 'every 10 seconds'), (30, 'every 30 seconds'),
                        (60, 'every minute'), (120, 'every 2 minutes'),
                        (300, 'every 5 minutes')]

    default_summary = forms.CharField(
        max_length=300, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-summary',
            'placeholder': 'e.g. Copyedit and formatting',
        }),
        label='Default edit summary',
        help_text='Pre-filled in the edit summary box. You can still change it per edit.',
    )
    initial_mode = forms.ChoiceField(choices=MODE_CHOICES, initial='wysiwyg',
                                     label='Editor opens in')
    toolbar = forms.ChoiceField(choices=TOOLBAR_CHOICES, initial='full',
                                label='Toolbar')
    theme = forms.ChoiceField(choices=THEME_CHOICES, initial='light',
                              label='Editor theme')
    autosave = forms.BooleanField(
        required=False, initial=True,
        label='Autosave drafts',
        help_text='Keep a local draft of your work in this browser while you type.',
    )
    autosave_interval = forms.TypedChoiceField(
        choices=INTERVAL_CHOICES, coerce=int, initial=30,
        label='Autosave frequency',
    )
    uploads = forms.BooleanField(
        required=False, initial=True,
        label='Image uploads enabled',
        help_text='Show the image buttons in the editor toolbar.',
    )

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        if profile is not None and not self.is_bound:
            prefs = profile.editor_prefs
            self.initial.update({
                'default_summary': prefs.get('default_summary', ''),
                'initial_mode': prefs.get('initial_mode', 'wysiwyg'),
                'toolbar': prefs.get('toolbar', 'full'),
                'theme': prefs.get('theme', 'light'),
                'autosave': bool(prefs.get('autosave', True)),
                'autosave_interval': prefs.get('autosave_interval', 30),
                'uploads': bool(prefs.get('uploads', True)),
            })

    def cleaned_settings(self):
        data = self.cleaned_data
        return {
            'default_summary': data['default_summary'].strip(),
            'initial_mode': data['initial_mode'],
            'toolbar': data['toolbar'],
            'theme': data['theme'],
            'autosave': bool(data['autosave']),
            'autosave_interval': int(data['autosave_interval']),
            'uploads': bool(data['uploads']),
        }


class RoleForm(forms.Form):
    """Admin form for changing another editor's role / access."""

    user_id = forms.IntegerField(widget=forms.HiddenInput)
    role = forms.ChoiceField(choices=[(k, v.split(' —')[0]) for k, v in Profile.ROLE_CHOICES],
                             widget=forms.Select(attrs={'class': 'input-summary'}))
    is_blocked = forms.BooleanField(required=False, label='Blocked')

    def clean_user_id(self):
        try:
            user = User.objects.get(pk=self.cleaned_data['user_id'])
        except User.DoesNotExist:
            raise forms.ValidationError('Unknown account.')
        return user.pk
