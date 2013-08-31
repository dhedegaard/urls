from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'app.views.index'),
    url(r'^(?P<keyword>.+)$', 'app.views.redirector'),
)
