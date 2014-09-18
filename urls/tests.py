from __future__ import absolute_import

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Url


class ModelsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            'testuser',
            'test@mail.com',
            'testpass',
        )

    def test_unicode(self):
        keyword = Url.objects.create(
            keyword='testkeyword',
            url='http://www.testurl.com/',
            proxy=True,
            user=self.user,
        )

        self.assertEqual(str(keyword),
                         u'keyword: testkeyword, url: http://www.testurl.com/'
                         u', proxy: True, public: False')


class ViewsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            'testuser',
            'test@mail.com',
            'testpass',
        )
        self.keyword = Url.objects.create(
            keyword='test-keyword', url='http://www.google.com/',
            user=self.user)
        self.keyword_proxy = Url.objects.create(
            keyword='test-proxy-keyword', url='http://www.google.com/',
            user=self.user, proxy=True)

    def _login(self):
        self.client.login(username='testuser', password='testpass')

    def test_list(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_login(self):
        response = self.client.get('/accounts/login/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_create_not_loggedin(self):
        response = self.client.get('/create')
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(
            '/accounts/login/?next=/create'))

    def test_non_existing_keyword(self):
        response = self.client.get('/non-existing-keyword')
        self.assertEquals(response.status_code, 404)

    def test_existing_keyword(self):
        response = self.client.get('/test-keyword')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], 'http://www.google.com/')

    def test_existing_proxy_keyword(self):
        response = self.client.get('/test-proxy-keyword')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/html'))

    def test_delete_nonexistant_keyword(self):
        keyword = self.keyword.keyword
        self.keyword.delete()

        self._login()
        response = self.client.post('/delete/%s/' % keyword)
        self.assertEqual(response.status_code, 404)

    def test_delete_keywork(self):
        self._login()
        response = self.client.post('/delete/%s' % self.keyword.keyword)

        self.assertRedirects(response, '/')
        self.assertFalse(Url.objects.filter(pk=self.keyword.pk).exists())

    def test_create_keyword(self):
        self._login()
        response = self.client.get('/create')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create.html')

    def test_create_keyword_submit(self):
        self._login()
        response = self.client.post('/create', {
            'keyword': 'test-keyword123',
            'url': 'http://www.testurl.com/',
        })

        self.assertRedirects(response, '/')
        new_keyword = Url.objects.get(keyword='test-keyword123')
        self.assertEqual(new_keyword.url, 'http://www.testurl.com/')
        self.assertEqual(new_keyword.user, self.user)


    def test_create_keyword_submit_slugify(self):
        self._login()
        response = self.client.post('/create', {
            'keyword': 'many weird Characters !"##%"%.',
            'url': 'http://testsite.com/',
            'slugify': 'on',
        })

        self.assertRedirects(response, '/')
        new_keyword = Url.objects.get(keyword='many-weird-characters')
        self.assertEqual(new_keyword.keyword, 'many-weird-characters')
        self.assertEqual(new_keyword.url, 'http://testsite.com/')

    def test_create_keyword_submit_already_exists(self):
        self._login()
        response = self.client.post('/create', {
            'keyword': self.keyword.keyword,
            'url': 'http://www.testurl.com/',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'keyword',
                             u'Keyword already exists.')

    def test_create_keyword_submit_empty_url(self):
        self._login()
        response = self.client.post('/create', {
            'keyword': 'testkeyword123',
            'url': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'url',
                             u'This field is required.')

    def test_create_keyword_used_by_system(self):
        self._login()
        response = self.client.post('/create', {
            'keyword': 'create',
            'url': 'http://www.testurl.com/',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'keyword',
                             u'Keyword is used by an internal URL of the '
                             u'system')

    def test_edit_keyword(self):
        self._login()
        response = self.client.get('/edit/%s' % self.keyword.keyword)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create.html')

    def test_edit_keyword_submit(self):
        self._login()
        response = self.client.post('/edit/%s' % self.keyword.keyword, {
            'keyword': 'new-testkeyword',
            'url': 'http://www.newtesturl.com/',
        })

        self.assertRedirects(response, '/')
        self.assertFalse(Url.objects.filter(pk=self.keyword.pk).exists())
        new_keyword = Url.objects.get(keyword='new-testkeyword')
        self.assertEqual(new_keyword.keyword, 'new-testkeyword')
        self.assertEqual(new_keyword.url, 'http://www.newtesturl.com/')

    def test_edit_keyword_submit_already_exists(self):
        self._login()
        response = self.client.post('/edit/%s' % self.keyword.keyword, {
            'keyword': self.keyword_proxy.keyword,
            'url': self.keyword.url,
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'keyword',
                             u'Keyword already exists.')

    def test_logout(self):
        self._login()
        response = self.client.post('/logout')

        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)
