from __future__ import absolute_import, unicode_literals

from django import forms
from django.core.validators import URLValidator
from django.utils.text import slugify as slugify_func
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit

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
        fields = [
            'keyword',
            'slugify',
            'url',
            'proxy',
            'public',
        ]
        widgets = {
            'keyword': forms.TextInput,
        }

    def __init__(self, *args, **kwargs):
        super(UrlForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            'keyword',
            Div('slugify', css_class='col-sm-offset-2 col-sm-10'),
            'url',
            Div('proxy', css_class='col-sm-offset-2 col-sm-10'),
            Div('public', css_class='col-sm-offset-2 col-sm-10'),
            Div(
                Submit('submit', 'Save', css_class='btn-primary'),
                css_class='col-sm-offset-2 col-sm-6',
            ),
        )

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
