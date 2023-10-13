from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import URLPattern

from . import views

urlpatterns: list[URLPattern] = [
    url(r"^create$", views.create, name="create"),
    url(
        r"^accounts/login/$",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="urls_login",
    ),
    url(r"^logout$", auth_views.LogoutView.as_view(next_page="/"), name="urls_logout"),
    url(r"^$", views.list, name="list"),
    url(r"^(?P<keyword>.+)/delete/$", views.delete, name="delete"),
    url(r"^(?P<keyword>.+)/edit/$", views.create, name="edit"),
    url(r"^(?P<keyword>.+)$", views.redirector, name="redirector"),
]
