from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from . import search as search_mod
from .models import Article, Category, Revision

BRIDGE_HTML = '''
<p>The <strong>Bandra Worli Sea Link</strong> crosses Mahim Bay. See also
[[Missing Page Title]] and <a href="/wiki/missing-page/">missing page</a>.</p>
<h2 id="design">Design</h2>
<p>Cable-stayed with steel stay cables.</p>
'''


def make_article(title='Test Bridge', content=None, **kwargs):
    article = Article(
        title=title,
        summary=kwargs.pop('summary', 'A test bridge article.'),
        content=content if content is not None else BRIDGE_HTML,
        **kwargs,
    )
    article.save_with_revision(summary='Initial version')
    return article


class CorePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = make_article()

    def test_home_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to Pedia')
        self.assertContains(response, 'Sign in to edit')

    def test_article_renders_with_toc_and_anchor(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Bridge')
        self.assertContains(response, 'class="toc')
        self.assertContains(response, 'id="design"')

    def test_article_shows_category_chips(self):
        category = Category.objects.create(name='Testing')
        self.article.categories.add(category)
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, 'Testing')

    def test_missing_article_is_404(self):
        response = self.client.get('/wiki/no-such-page/')
        self.assertEqual(response.status_code, 404)

    def test_search_finds_article(self):
        response = self.client.get('/search/', {'q': 'Bandra'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Bridge')

    def test_recent_changes_page(self):
        response = self.client.get('/recent/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Initial version')

    def test_categories_and_category_page(self):
        category = Category.objects.create(name='Testing', description='Tests.')
        self.article.categories.add(category)
        self.assertEqual(self.client.get('/categories/').status_code, 200)
        detail = self.client.get(category.get_absolute_url())
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'Test Bridge')

    def test_random_redirects_to_article(self):
        response = self.client.get('/random/')
        self.assertEqual(response.status_code, 302)

    def test_red_link_for_missing_page(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, 'class="new"')

    def test_wikilink_resolves_to_existing_page(self):
        target = make_article(title='Missing Page Title')
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, target.get_absolute_url())

    def test_history_and_diff(self):
        url = self.article.get_absolute_url()
        self.assertEqual(self.client.get(url + 'history/').status_code, 200)
        response = self.client.get(url + 'history/diff/')
        self.assertEqual(response.status_code, 200)

    def test_history_diff_between_revisions(self):
        first = self.article.revisions.first()
        second_rev = self.article
        second_rev.content = '<p>Changed body.</p>'
        second_rev.save_with_revision(summary='Change')
        url = (f"{self.article.get_absolute_url()}history/diff/"
               f"?old={first.pk}&new=current")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Changed body')

    def test_search_fts_indexed(self):
        results = search_mod.search_articles('Bandra')
        self.assertTrue(results)

    def test_plain_text_extracted(self):
        self.assertIn('steel stay cables', self.article.text_content)


class AnonymousGatingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = make_article()

    def assertLoginRedirect(self, path, method='get'):
        response = getattr(self.client, method)(path)
        self.assertEqual(response.status_code, 302, path)
        self.assertTrue(response.url.startswith('/accounts/login/'),
                        f'{path} -> {response.url}')

    def assertHomeRedirect(self, path, method='get'):
        response = getattr(self.client, method)(path)
        self.assertEqual(response.status_code, 302, path)
        self.assertEqual(response.url, '/', f'{path} -> {response.url}')

    def test_anon_edit_goes_to_login(self):
        self.assertLoginRedirect(self.article.get_absolute_url() + 'edit/')

    def test_anon_create_goes_to_login(self):
        self.assertLoginRedirect('/new/')

    def test_anon_review_goes_to_login(self):
        self.assertLoginRedirect('/review/')

    def test_anon_feature_goes_to_login(self):
        self.assertLoginRedirect(self.article.get_absolute_url() + 'feature/',
                                 method='post')

    def test_anon_settings_goes_to_login(self):
        self.assertLoginRedirect('/accounts/settings/')

    def test_anon_people_goes_home(self):
        self.assertHomeRedirect('/accounts/people/')

    def test_anon_sees_login_tab_not_edit_tab(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, 'Log in to edit')
        self.assertNotContains(response, '">Edit</a>')

    def test_anon_cannot_see_pending_draft(self):
        draft = make_article(title='Hidden Draft', is_pending=True)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_anon_upload_requires_login(self):
        response = self.client.post('/api/upload/image/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_anon_does_not_see_pending_revision_in_history(self):
        editor = User.objects.create_user('hopper', password='Copper-Lantern-9182!')
        Revision.create_pending(self.article, content='<p>queued</p>',
                                summary='queued', editor=editor,
                                proposed_title=self.article.title)
        response = self.client.get(self.article.get_absolute_url() + 'history/')
        self.assertNotContains(response, 'queued')


class RegistrationTests(TestCase):
    def register(self, username, password='Marble-Compass-4471!'):
        return self.client.post('/accounts/register/', {
            'username': username,
            'password1': password,
            'password2': password,
        })

    def test_first_account_becomes_admin(self):
        response = self.register('boss')
        self.assertEqual(response.status_code, 302)
        profile = User.objects.get(username='boss').profile
        self.assertEqual(profile.role, 'admin')
        self.assertTrue(User.objects.get(username='boss').is_staff)

    def test_later_accounts_are_editors(self):
        self.register('boss')
        self.client.logout()
        self.register('scribe')
        self.assertEqual(User.objects.get(username='scribe').profile.role, 'editor')

    def test_duplicate_username_rejected(self):
        self.register('boss')
        self.client.logout()
        response = self.register('boss')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'errorlist')

    def test_login_and_logout(self):
        User.objects.create_user('boss', password='Marble-Compass-4471!')
        self.assertTrue(self.client.login(username='boss',
                                          password='Marble-Compass-4471!'))
        logout = self.client.post('/accounts/logout/')
        self.assertEqual(logout.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_requires_post(self):
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 405)


class EditorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = make_article()
        cls.editor = User.objects.create_user('scribe',
                                              password='Marble-Compass-4471!')
        cls.editor.profile.role = 'editor'
        cls.editor.profile.save()

    def setUp(self):
        self.client.force_login(self.editor)

    def test_edit_form_shows_review_notice_and_label(self):
        response = self.client.get(self.article.get_absolute_url() + 'edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'review queue')
        self.assertContains(response, 'Submit for review')
        self.assertContains(response, 'go to the')

    def test_editor_edit_is_queued_not_published(self):
        response = self.client.post(self.article.get_absolute_url() + 'edit/', {
            'title': self.article.title,
            'summary': 'new summary',
            'content': '<p>Proposed body text.</p>',
            'edit_summary': 'please publish',
        })
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertIn('Bandra Worli Sea Link', self.article.content)
        pending = self.article.revisions.filter(status=Revision.STATUS_PENDING)
        self.assertEqual(pending.count(), 1)
        revision = pending.get()
        self.assertEqual(revision.editor, self.editor)
        self.assertEqual(revision.proposed_title, self.article.title)
        self.assertIn('Proposed body text', revision.content)

    def test_editor_sees_own_pending_revision_in_history(self):
        Revision.create_pending(self.article, content='<p>mine only</p>',
                                summary='my queued edit', editor=self.editor,
                                proposed_title=self.article.title)
        response = self.client.get(self.article.get_absolute_url() + 'history/')
        self.assertContains(response, 'my queued edit')
        self.assertContains(response, 'pending')

    def test_editor_review_queue_redirects_home(self):
        response = self.client.get('/review/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_editor_cannot_feature_article(self):
        response = self.client.post(self.article.get_absolute_url() + 'feature/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_featured)

    def test_editor_creates_draft_pending_review(self):
        response = self.client.post('/new/', {
            'title': 'Queued Draft',
            'summary': 'draft summary',
            'content': '<p>Draft body.</p>',
            'edit_summary': 'new page',
        })
        self.assertEqual(response.status_code, 302)
        draft = Article.objects.get(title='Queued Draft')
        self.assertTrue(draft.is_pending)
        self.assertEqual(draft.created_by, self.editor)
        self.assertEqual(draft.revisions.filter(
            status=Revision.STATUS_PENDING).count(), 1)

    def test_editor_sees_own_draft_but_anon_does_not(self):
        draft = Article.objects.create(title='Private Draft',
                                       content='<p>secret</p>',
                                       is_pending=True, created_by=self.editor)
        draft.save_with_revision(summary='draft', editor=self.editor,
                                 status=Revision.STATUS_PENDING)
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)

    def test_editor_revert_is_queued(self):
        first = self.article.revisions.first()
        response = self.client.post(
            self.article.get_absolute_url() + f'history/{first.pk}/revert/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.article.revisions.filter(
            status=Revision.STATUS_PENDING).count(), 1)

    def test_editor_upload_allowed(self):
        import base64
        from django.core.files.uploadedfile import SimpleUploadedFile
        png = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8'
            'z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
        upload = SimpleUploadedFile('px.png', png, content_type='image/png')
        response = self.client.post('/api/upload/image/', {'file': upload})
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())


class ViewerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = make_article()
        cls.viewer = User.objects.create_user('reader',
                                              password='Amber-Anchor-6350!')
        cls.viewer.profile.role = 'viewer'
        cls.viewer.profile.save()

    def setUp(self):
        self.client.force_login(self.viewer)

    def test_viewer_home_is_read_only(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'read-only access')

    def test_viewer_cannot_edit(self):
        response = self.client.get(self.article.get_absolute_url() + 'edit/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_viewer_cannot_create(self):
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_viewer_cannot_open_review(self):
        response = self.client.get('/review/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_viewer_article_page_has_no_edit_tab(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertNotContains(response, '">Edit</a>')


class AdminModerationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('boss',
                                              password='Copper-Lantern-9182!')
        self.assertTrue(self.admin.profile.role == 'admin')
        self.editor = User.objects.create_user('scribe',
                                               password='Marble-Compass-4471!')
        self.editor.profile.role = 'editor'
        self.editor.profile.save()
        self.article = make_article()

    def test_admin_edit_publishes_immediately(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.article.get_absolute_url() + 'edit/', {
            'title': 'Test Bridge',
            'summary': 'updated',
            'content': '<p>Admin published body.</p>',
            'edit_summary': 'direct publish',
        })
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertIn('Admin published body', self.article.content)
        latest = self.article.revisions.first()
        self.assertEqual(latest.status, Revision.STATUS_APPROVED)
        self.assertEqual(latest.editor, self.admin)

    def test_admin_approves_editor_edit(self):
        self.client.force_login(self.editor)
        self.client.post(self.article.get_absolute_url() + 'edit/', {
            'title': 'Test Bridge Renamed',
            'summary': 'renamed summary',
            'content': '<p>Approved body.</p>',
            'edit_summary': 'rename',
        })
        self.client.logout()

        self.client.force_login(self.admin)
        queue = self.client.get('/review/')
        self.assertContains(queue, 'Test Bridge')
        pending = self.article.revisions.get(status=Revision.STATUS_PENDING)
        response = self.client.post(f'/review/revision/{pending.pk}/',
                                    {'action': 'approve'})
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertIn('Approved body', self.article.content)
        self.assertEqual(self.article.title, 'Test Bridge Renamed')
        self.assertEqual(self.article.summary, 'renamed summary')
        pending.refresh_from_db()
        self.assertEqual(pending.status, Revision.STATUS_APPROVED)
        self.assertEqual(pending.reviewed_by, self.admin)

    def test_admin_rejects_editor_edit(self):
        original = self.article.content
        self.client.force_login(self.editor)
        self.client.post(self.article.get_absolute_url() + 'edit/', {
            'title': 'Test Bridge',
            'summary': 'nope',
            'content': '<p>Rejected body.</p>',
            'edit_summary': 'bad edit',
        })
        self.client.logout()

        self.client.force_login(self.admin)
        pending = self.article.revisions.get(status=Revision.STATUS_PENDING)
        response = self.client.post(f'/review/revision/{pending.pk}/',
                                    {'action': 'reject'})
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, original)
        pending.refresh_from_db()
        self.assertEqual(pending.status, Revision.STATUS_REJECTED)
        self.assertEqual(pending.reviewed_by, self.admin)

    def test_admin_publishes_draft(self):
        self.client.force_login(self.editor)
        self.client.post('/new/', {
            'title': 'Brand New Page',
            'summary': 'draft',
            'content': '<p>Draft body.</p>',
            'edit_summary': 'new',
        })
        self.client.logout()

        draft = Article.objects.get(title='Brand New Page')
        self.assertTrue(draft.is_pending)
        self.client.force_login(self.admin)
        queue = self.client.get('/review/')
        self.assertContains(queue, 'Brand New Page')
        response = self.client.post(f'/review/draft/{draft.pk}/',
                                    {'action': 'approve'})
        self.assertEqual(response.status_code, 302)
        draft.refresh_from_db()
        self.assertFalse(draft.is_pending)
        self.assertEqual(draft.revisions.filter(
            status=Revision.STATUS_APPROVED).count(), 1)

    def test_admin_rejects_draft_deletes_it(self):
        self.client.force_login(self.editor)
        self.client.post('/new/', {
            'title': 'Doomed Page',
            'summary': 'draft',
            'content': '<p>Nope.</p>',
            'edit_summary': 'new',
        })
        self.client.logout()
        draft = Article.objects.get(title='Doomed Page')

        self.client.force_login(self.admin)
        self.client.post(f'/review/draft/{draft.pk}/', {'action': 'reject'})
        self.assertFalse(Article.objects.filter(pk=draft.pk).exists())

    def test_featured_toggle(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.article.get_absolute_url() + 'feature/')
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertTrue(self.article.is_featured)
        self.client.post(self.article.get_absolute_url() + 'feature/')
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_featured)

    def test_draft_hidden_from_everyone_except_admin_and_author(self):
        draft = Article.objects.create(title='Admin Only Draft',
                                       content='<p>secret</p>',
                                       is_pending=True, created_by=self.editor)
        draft.save_with_revision(summary='draft', editor=self.editor,
                                 status=Revision.STATUS_PENDING)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 200)
        self.client.force_login(User.objects.create_user(
            'nosy', password='Amber-Anchor-6350!'))
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)

    def test_blocked_editor_cannot_edit(self):
        self.editor.profile.is_blocked = True
        self.editor.profile.save()
        self.client.force_login(self.editor)
        response = self.client.get(self.article.get_absolute_url() + 'edit/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')


class PeopleManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('boss',
                                              password='Copper-Lantern-9182!')
        self.editor = User.objects.create_user('scribe',
                                               password='Marble-Compass-4471!')
        self.editor.profile.role = 'editor'
        self.editor.profile.save()
        self.client.force_login(self.admin)

    def test_people_page_lists_accounts(self):
        response = self.client.get('/accounts/people/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'boss')
        self.assertContains(response, 'scribe')

    def test_role_change_and_promotion(self):
        response = self.client.post('/accounts/people/', {
            'user_id': self.editor.pk,
            'role': 'viewer',
        })
        self.assertEqual(response.status_code, 302)
        self.editor.profile.refresh_from_db()
        self.assertEqual(self.editor.profile.role, 'viewer')

        self.client.post('/accounts/people/', {
            'user_id': self.editor.pk,
            'role': 'admin',
        })
        self.editor.profile.refresh_from_db()
        self.assertEqual(self.editor.profile.role, 'admin')
        self.editor.refresh_from_db()
        self.assertTrue(self.editor.is_staff)

    def test_cannot_demote_last_admin(self):
        response = self.client.post('/accounts/people/', {
            'user_id': self.admin.pk,
            'role': 'editor',
        })
        self.assertRedirects(response, '/accounts/people/',
                             fetch_redirect_response=False)
        self.admin.profile.refresh_from_db()
        self.assertEqual(self.admin.profile.role, 'admin')

    def test_blocking_editor(self):
        self.client.post('/accounts/people/', {
            'user_id': self.editor.pk,
            'role': 'editor',
            'is_blocked': 'on',
        })
        self.editor.profile.refresh_from_db()
        self.assertTrue(self.editor.profile.is_blocked)

    def test_non_admin_redirected_from_people(self):
        self.client.force_login(self.editor)
        response = self.client.get('/accounts/people/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')


class SettingsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('boss',
                                              password='Copper-Lantern-9182!')

    def test_settings_requires_login(self):
        self.client.logout()
        response = self.client.get('/accounts/settings/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_settings_page_renders(self):
        self.client.force_login(self.admin)
        response = self.client.get('/accounts/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editor settings')
        self.assertContains(response, 'Default edit summary')

    def test_settings_save_persists(self):
        self.client.force_login(self.admin)
        response = self.client.post('/accounts/settings/', {
            'default_summary': 'Copied from the source page',
            'initial_mode': 'markdown',
            'toolbar': 'compact',
            'theme': 'dark',
            'autosave': 'on',
            'autosave_interval': 60,
            'uploads': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.admin.profile.refresh_from_db()
        self.assertEqual(self.admin.profile.setting('default_summary'),
                         'Copied from the source page')
        self.assertEqual(self.admin.profile.setting('theme'), 'dark')
        self.assertEqual(self.admin.profile.setting('toolbar'), 'compact')
        self.assertEqual(self.admin.profile.setting('autosave_interval'), 60)

    def test_default_summary_pre_fills_edit_form(self):
        self.admin.profile.editor_settings = {
            'default_summary': 'My usual summary',
        }
        self.admin.profile.save()
        self.client.force_login(self.admin)
        article = make_article()
        response = self.client.get(article.get_absolute_url() + 'edit/')
        self.assertContains(response, 'My usual summary')

    def test_anonymous_settings_uses_defaults(self):
        self.client.force_login(self.admin)
        article = make_article()
        self.client.logout()
        response = self.client.get(article.get_absolute_url() + 'edit/')
        self.assertEqual(response.status_code, 302)
