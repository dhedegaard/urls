from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^create$', 'urls.views.create', name='create'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout$', 'urls.views.logout', name='logout'),
    url(r'^$', 'urls.views.list', name='list'),
    url(r'^delete/(?P<keyword>.+)$', 'urls.views.delete', name='delete'),
    url(r'^edit/(?P<keyword>.+)$', 'urls.views.create', name='edit'),
    url(r'^(?P<keyword>.+)$', 'urls.views.redirector', name='redirector'),
)
