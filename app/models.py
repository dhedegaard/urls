from django.db import models
from django.contrib.auth.models import User


class Url(models.Model):
    keyword = models.TextField(max_length=100, primary_key=True)
    url = models.TextField(max_length=2048, null=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, db_column='user')
    proxy = models.BooleanField(default=False)

    def __unicode__(self):
        return 'keyword: %s, url: %s, created: %s, user: %s, proxy: %s' % (
            self.keyword, self.url, self.created, self.user.username, self.proxy,
        )

    class Meta:
        ordering = ['keyword']