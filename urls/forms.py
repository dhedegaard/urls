import re

from django import forms
from django.core.validators import URLValidator

from .models import Url
from .urls import urlpatterns

MATCH_SLUG = re.compile(r'^[a-z0-9][a-z0-9-\.]+[a-z0-9]$')


class UrlForm(forms.ModelForm):
    url = forms.CharField(
        required=True, max_length=Url._meta.get_field('url').max_length,
        validators=[URLValidator()])

    class Meta:
        model = Url
        exclude = ['created', 'user']

    def clean_keyword(self):
        keyword = self.cleaned_data['keyword']

        keyword_exists = Url.objects.filter(keyword=keyword).exists()

        # Don't allow an existing url to change keyword to another existing
        # keyword.
        if self.instance and\
           self.instance.keyword != keyword and\
           keyword_exists:
            raise forms.ValidationError('keyword already exists!')

        # Don't allow creating a new url with an existing keyword.
        if self.instance.pk is None and\
           keyword_exists:
            raise forms.ValidationError('keyword already exists: %s' % keyword)

        if not MATCH_SLUG.match(keyword):
            raise forms.ValidationError(
                'keyword is not a-z, 0-9, dots and dashes: %s' % keyword)

        # Make sure not to match any of the URL's currently matched.
        for url in urlpatterns:
            if url.name != 'redirector' and url.regex.findall(keyword):
                raise forms.ValidationError(
                    'Keyword is used by an internal URL of the system')

        return keyword
