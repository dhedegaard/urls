from __future__ import absolute_import, unicode_literals

from django import forms
from django.core.validators import URLValidator
from django.utils.text import slugify as slugify_func

from .models import Url
from .urls import urlpatterns


class UrlForm(forms.ModelForm):
    url = forms.CharField(
        required=True, max_length=Url._meta.get_field('url').max_length,
        validators=[URLValidator()])
    slugify = forms.BooleanField(
        label='Slugify the keyword ?', required=False)

    class Meta:
        model = Url
        exclude = ['created', 'user']

    def clean(self):
        super(UrlForm, self).clean()
        if any(self.errors):
            return
        data = self.cleaned_data
        keyword = data['keyword']

        # Slugify the keyword, if needed.
        if data['slugify'] and keyword:
            data['keyword'] = keyword = slugify_func(data['keyword'])

        keyword_already_exists = Url.objects.filter(keyword=keyword).exists()

        if self.instance and self.instance.keyword != keyword and\
           keyword_already_exists:
            self.add_error('keyword', 'Keyword already exists.')

        # Make sure not to match any non-redirector URL's from the urls module.
        for url in urlpatterns:
            if url.name != 'redirector' and url.regex.findall(keyword):
                self.add_error(
                    'keyword', ('Keyword is used by an internal '
                                'URL of the system'))

        return data
