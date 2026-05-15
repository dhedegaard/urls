from django.contrib.auth import views as auth_views
from django.urls import URLPattern, path, re_path

from . import views

urlpatterns: list[URLPattern] = [
    path("create", views.create, name="create"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="login.html"), name="urls_login"),
    path("logout", auth_views.LogoutView.as_view(next_page="/"), name="urls_logout"),
    path("", views.list, name="list"),
    re_path(r"^(?P<keyword>.+)/delete/$", views.delete, name="delete"),
    re_path(r"^(?P<keyword>.+)/edit/$", views.create, name="edit"),
    re_path(r"^(?P<keyword>.+)$", views.redirector, name="redirector"),
]
