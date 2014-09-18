from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Url(models.Model):
    keyword = models.TextField(max_length=100, primary_key=True)
    url = models.TextField(
        verbose_name='URL', max_length=2048, null=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, db_column='user')
    proxy = models.BooleanField(
        verbose_name='Proxy requests', default=False)
    public = models.BooleanField(
        verbose_name='Public redirect', default=False)

    def __unicode__(self):
        return ('keyword: %s, url: %s, proxy: %s, public: %s' % (
            self.keyword, self.url, self.proxy, self.public,
        ))

    class Meta:
        ordering = ['keyword']
