import django.contrib.auth.views
from django.core.urlresolvers import resolve
from django.test import TestCase
from django.contrib.auth.models import User

from app import views, models


class UrlPatternsTests(TestCase):
    def testList(self):
        listview = resolve('/')
        self.assertEquals(listview.func, views.list)

    def testCreate(self):
        createview = resolve('/create')
        self.assertEquals(createview.func, views.create)

    def testLogin(self):
        loginview = resolve('/accounts/login/')
        self.assertEquals(loginview.func, django.contrib.auth.views.login)

    def testLogout(self):
        logoutview = resolve('/logout')
        self.assertEquals(logoutview.func, views.logout)

    def testDelete(self):
        deleteview = resolve('/delete/keyword')
        self.assertEquals(deleteview.func, views.delete)

    def testEdit(self):
        editview = resolve('/edit/keyword')
        self.assertEquals(editview.func, views.create)

    def testKeyword(self):
        keywordview = resolve('/keyword')
        self.assertEquals(keywordview.func, views.redirector)

class ClientTests(TestCase):
    def setUp(self):
        user = User.objects.create(
            username='testuser', password='test123')
        models.Url.objects.create(
            keyword='new-keyword', url='http://www.google.com/',
            user=user)
        models.Url.objects.create(
            keyword='new-proxy-keyword', url='http://www.google.com/',
            user=user, proxy=True)

    def tearDown(self):
        User.objects.filter(username='testuser').delete()
        models.Url.objects.filter(
            keyword='new-keyword', url='http://www.google.com/').delete()

    def testList(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def testLogin(self):
        response = self.client.get('/accounts/login/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def testCreateNotLoggedIn(self):
        response = self.client.get('/create')
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(
            '/accounts/login/?next=/create'))

    def testEditNotLoggedIn(self):
        response = self.client.get('/create')
        self.assertEquals(response.status_code, 302)

    def testNonExistingKeyword(self):
        response = self.client.get('/non-existing-keyword')
        self.assertEquals(response.status_code, 404)

    def testExistingKeyword(self):
        response = self.client.get('/new-keyword')
        self.assertEquals(response.status_code, 301)
        self.assertEquals(response['Location'], 'http://www.google.com/')

    def testExistingProxyKeyword(self):
        response = self.client.get('/new-proxy-keyword')
        self.assertEquals(response.status_code, 200)
        # The Content-Type from the proxied URL should be returned to the
        # client.
        self.assertTrue(response['Content-Type'].startswith('text/html'))