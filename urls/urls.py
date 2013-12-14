from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       url(r'^$', 'app.views.index', name='index'),
                       url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
                       url(r'^logout$', 'app.views.logout', name='logout'),
                       url(r'^list$', 'app.views.list', name='list'),
                       url(r'^delete$', 'app.views.delete', name='delete'),
                       url(r'^(?P<keyword>.+)$', 'app.views.redirector', name='redirector'),
)
