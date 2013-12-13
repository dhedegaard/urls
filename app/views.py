import requests
from django.shortcuts import render
from django.http import (
    HttpResponseNotFound,
    HttpResponsePermanentRedirect,
    HttpResponse,
    HttpResponseServerError,
    )

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
            url = form.save(commit=False)
            url.ipaddress = _get_client_ip(request)
            url.save()

            created_keyword = url.keyword
            form = UrlForm()
    else:
        form = UrlForm()
    return render(request, 'index.html', {
        'form': form,
        'created_keyword': created_keyword,
        'redirect_count': Url.objects.all().count(),
    })


def _redirect_proxy(url):
    try:
        r = requests.get(url.url)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectionError) as e:
        return HttpResponseServerError('%s' % e.message)
    return HttpResponse(r.text, mimetype=r.headers.get('Content-Type', 'text/plain'))


def redirector(request, keyword):
    try:
        url = Url.objects.get(keyword=keyword)
        if url.proxy:
            return _redirect_proxy(url)
        else:
            return HttpResponsePermanentRedirect(url.url)
    except Url.DoesNotExist:
        return HttpResponseNotFound('No URL found for keyword: %s' % keyword)