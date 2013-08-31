from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect

from .forms import UrlForm
from .models import Url


def _get_client_ip(request):
    '''
    Returns the client IP address from a request.UrlForm

    :param request: A django response object.
    :returns: IP of the client of the the request, as a string.
    '''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


def index(request):
    created_keyword = None
    if request.method == 'POST':
        form = UrlForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            url = form.cleaned_data['url']
            ipaddress = _get_client_ip(request)

            Url(keyword=keyword, url=url, ipaddress=ipaddress).save()
            created_keyword = keyword
            form = UrlForm()
    else:
        form = UrlForm()
    return render(request, 'index.html', {
        'form': form,
        'created_keyword': created_keyword,
        'redirect_count': Url.objects.all().count(),
    })


def redirector(request, keyword):
    try:
        url = Url.objects.get(keyword=keyword)
        return HttpResponsePermanentRedirect(url.url)
    except Url.DoesNotExist:
        return HttpResponseNotFound('No URL found for keyword: %s' % keyword)