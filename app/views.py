import requests
from django.shortcuts import render, redirect
from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
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


def logout(request):
    logout_user(request)
    return redirect('list')


def list(request):
    return render(request, 'list.html', {
        'urls': Url.objects.select_related().all(),
        'title': 'List',
    })


@login_required
def delete(request):
    if 'keyword' not in request.POST:
        return redirect('list')

    url = Url.objects.get(keyword=request.POST['keyword'])
    url.delete()
    return redirect('list')


@login_required
def create(request):
    created_keyword = None
    if request.method == 'POST':
        form = UrlForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.user = request.user
            url.save()

            created_keyword = url.keyword
            form = UrlForm()
    else:
        form = UrlForm()
    return render(request, 'create.html', {
        'form': form,
        'created_keyword': created_keyword,
        'redirect_count': Url.objects.all().count(),
        'title': 'Create',
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