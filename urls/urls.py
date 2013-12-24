from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^create$', 'app.views.create', name='create'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
    	{'template_name': 'login.html'}, name='login'),
    url(r'^logout$', 'app.views.logout', name='logout'),
    url(r'^$', 'app.views.list', name='list'),
    url(r'^delete$', 'app.views.delete', name='delete'),
    url(r'^(?P<keyword>.+)$', 'app.views.redirector', name='redirector'),
)
