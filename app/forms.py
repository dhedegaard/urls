import re

from django import forms
from django.core.validators import URLValidator

from .models import Url

MATCH_SLUG = re.compile(r'^[a-z0-9][a-z0-9-][a-z0-9]+$')


class UrlForm(forms.ModelForm):
    url = forms.CharField(required=True, max_length=Url._meta.get_field('url').max_length,
                          validators=[URLValidator()])

    class Meta:
        model = Url
        exclude = ['created', 'user']

    def clean_keyword(self):
        keyword = self.cleaned_data['keyword']

        if Url.objects.filter(keyword=keyword).exists():
            raise forms.ValidationError('keyword already exists: %s' % keyword)

        if not MATCH_SLUG.match(keyword):
            raise forms.ValidationError('keyword is not a-z, 0-9 and dashes: %s' % keyword)

        return keyword