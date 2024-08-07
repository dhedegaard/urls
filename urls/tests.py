from __future__ import absolute_import, unicode_literals

from typing import cast
from unittest import mock
from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpResponseServerError
from django.urls import reverse
from requests.exceptions import ConnectionError
from django.forms import Form

from .models import Url
from .views import _redirect_proxy  # type: ignore


class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            "testuser",
            "test@mail.com",
            "testpass",
        )
        self.keyword = Url.objects.create(
            keyword="test-keyword", url="http://www.google.com/", user=self.user
        )
        self.keyword_proxy = Url.objects.create(
            keyword="test-proxy-keyword",
            url="http://www.google.com/",
            user=self.user,
            proxy=True,
        )

    def _login(self):
        self.client.login(username="testuser", password="testpass")

    def test_list(self):
        response = self.client.get(reverse("list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")

    def test_login(self):
        response = self.client.get(reverse("urls_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_create_not_loggedin(self):
        response = self.client.get(reverse("create"))
        self.assertRedirects(
            response,
            reverse("urls_login") + "?next=" + reverse("create"),
            fetch_redirect_response=False,
        )

    def test_non_existing_keyword(self):
        response = self.client.get(
            reverse(
                "redirector",
                kwargs={
                    "keyword": "non-existing-keyword",
                },
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_existing_keyword(self):
        response = self.client.get(
            reverse(
                "redirector",
                kwargs={
                    "keyword": "test-keyword",
                },
            )
        )
        self.assertRedirects(response, self.keyword.url, fetch_redirect_response=False)

    def test_existing_proxy_keyword(self):
        response = self.client.get(
            reverse(
                "redirector",
                kwargs={
                    "keyword": "test-proxy-keyword",
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"], "text/html")

    def test_delete_nonexistant_keyword(self):
        keyword = self.keyword.keyword
        self.keyword.delete()

        self._login()
        response = self.client.post(
            reverse(
                "delete",
                kwargs={
                    "keyword": keyword,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_keywork(self):
        self._login()
        response = self.client.post(
            reverse(
                "delete",
                kwargs={
                    "keyword": self.keyword.keyword,
                },
            )
        )

        self.assertRedirects(response, "/")
        self.assertFalse(Url.objects.filter(pk=self.keyword.pk).exists())

    def test_create_keyword(self):
        self._login()
        response = self.client.get(reverse("create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create.html")

    def test_create_keyword_submit(self):
        self._login()
        response = self.client.post(
            reverse("create"),
            {
                "keyword": "test-keyword123",
                "url": "http://www.testurl.com/",
            },
        )

        self.assertRedirects(response, reverse("list"))
        new_keyword = Url.objects.get(keyword="test-keyword123")
        self.assertEqual(new_keyword.url, "http://www.testurl.com/")
        self.assertEqual(new_keyword.user, self.user)

    def test_create_keyword_submit_slugify(self):
        self._login()
        response = self.client.post(
            reverse("create"),
            {
                "keyword": 'many weird Characters !"##%"%.',
                "url": "http://testsite.com/",
                "slugify": "on",
            },
        )

        self.assertRedirects(response, reverse("list"))
        new_keyword = Url.objects.get(keyword="many-weird-characters")
        self.assertEqual(new_keyword.keyword, "many-weird-characters")
        self.assertEqual(new_keyword.url, "http://testsite.com/")

    def test_create_keyword_submit_already_exists(self):
        self._login()
        response = self.client.post(
            reverse("create"),
            {
                "keyword": self.keyword.keyword,
                "url": "http://www.testurl.com/",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            cast(Form, response.context["form"]),
            "keyword",
            ["Keyword already exists."],
        )  # type: ignore

    def test_create_keyword_submit_empty_url(self):
        self._login()
        response = self.client.post(
            reverse("create"),
            {
                "keyword": "testkeyword123",
                "url": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            cast(Form, response.context["form"]), "url", "This field is required."
        )  # type: ignore

    def test_create_keyword_used_by_system(self):
        self._login()
        response = self.client.post(
            reverse("create"),
            {
                "keyword": "create",
                "url": "http://www.testurl.com/",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            cast(Form, response.context["form"]),
            "keyword",
            "Keyword is used by an internal URL of the system",
        )  # type: ignore

    def test_edit_keyword(self):
        self._login()
        response = self.client.get(
            reverse(
                "edit",
                kwargs={
                    "keyword": self.keyword.keyword,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create.html")

    def test_edit_keyword_submit(self):
        self._login()
        response = self.client.post(
            reverse(
                "edit",
                kwargs={
                    "keyword": self.keyword.keyword,
                },
            ),
            {
                "keyword": "new-testkeyword",
                "url": "http://www.newtesturl.com/",
            },
        )

        self.assertRedirects(response, reverse("list"))
        self.assertFalse(Url.objects.filter(pk=self.keyword.pk).exists())
        new_keyword = Url.objects.get(keyword="new-testkeyword")
        self.assertEqual(new_keyword.url, "http://www.newtesturl.com/")

    def test_edit_keyword_submit_already_exists(self):
        self._login()
        response = self.client.post(
            reverse(
                "edit",
                kwargs={
                    "keyword": self.keyword.keyword,
                },
            ),
            {
                "keyword": self.keyword_proxy.keyword,
                "url": self.keyword.url,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            cast(Form, response.context["form"]),
            "keyword",
            "Keyword already exists.",
        )  # type: ignore

    def test_logout(self):
        self._login()
        response = self.client.post(reverse("urls_logout"))

        self.assertRedirects(response, reverse("list"))
        self.assertNotIn("_auth_user_id", self.client.session)

    @mock.patch("urls.views.requests")
    def test_redirector__exception(self, requests_patch):  # type: ignore
        requests_patch.get.side_effect = ConnectionError("something bad happened")  # type: ignore
        requests_patch.exceptions.ConnectionError = ConnectionError  # type: ignore

        self.assertTrue(
            isinstance(_redirect_proxy("http://testserver/"), HttpResponseServerError)
        )
