from django.db import models


class Url(models.Model):
    keyword = models.TextField(max_length=100, primary_key=True)
    url = models.TextField(max_length=2048, null=False)
    created = models.DateTimeField(auto_now_add=True)
    ipaddress = models.TextField(max_length=15, null=False)
    proxy = models.BooleanField(default=False)

    def __unicode__(self):
        return 'keyword: %s, url: %s, created: %s, ipaddress: %s, proxy: %s' % (
            self.keyword, self.url, self.created, self.ipaddress, self.proxy,
        )