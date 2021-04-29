from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^create$', views.create, name='create'),
    url(r'^accounts/login/$', auth_views.LoginView, {
        'template_name': 'login.html',
    }, name='urls_login'),
    url(r'^logout$', auth_views.LogoutView, {
        'next_page': u'/',
    }, name='urls_logout'),
    url(r'^$', views.list, name='list'),
    url(r'^(?P<keyword>.+)/delete/$', views.delete, name='delete'),
    url(r'^(?P<keyword>.+)/edit/$', views.create, name='edit'),
    url(r'^(?P<keyword>.+)$', views.redirector, name='redirector'),
]
