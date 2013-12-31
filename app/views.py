import requests
from django.shortcuts import render, redirect
from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponsePermanentRedirect,
    HttpResponse,
    HttpResponseServerError,
    )
from django.db import transaction

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


def redirect_list(changed_keyword, changed_event_name):
    '''
    Redirects to the list url, with the given parameters.
    '''
    response = redirect('list')
    response['Location'] += '?changed_keyword=%s&changed_event_name=%s' % (
        changed_keyword, changed_event_name)
    return response


def list(request):
    urls = Url.objects.select_related().all()

    if not request.user.is_authenticated():
        urls = urls.filter(public=True)

    return render(request, 'list.html', {
        'urls': urls,
        'title': 'List',
        'changed_keyword': request.GET.get('changed_keyword'),
        'changed_event_name': request.GET.get('changed_event_name'),
    })


@login_required
@transaction.atomic
def delete(request, keyword):
    try:
        url = Url.objects.get(keyword=keyword)
    except Url.DoesNotExist:
        return HttpResponseBadRequest('keyword does not exist: %s' % keyword)
    url.delete()
    return redirect_list(keyword, 'deleted')


@login_required
@transaction.atomic
def create(request, keyword=None):
    if request.method == 'POST':
        if keyword is not None:
            # If we're editing, make sure to provide the existing instance.
            form = UrlForm(
                request.POST,
                instance=Url.objects.get(keyword=keyword))
        else:
            form = UrlForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.user = request.user
            url.save()

            return redirect_list(
                url.keyword,
                'created' if keyword is None else 'changed')
    else:
        if keyword is not None:
            form = UrlForm(instance=Url.objects.get(keyword=keyword))
        else:
            form = UrlForm()
    return render(request, 'create.html', {
        'form': form,
        'redirect_count': Url.objects.all().count(),
        'title': current_url.title(),
        'keyword': keyword,
    })


def _redirect_proxy(url):
    try:
        r = requests.get(url.url)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ConnectionError) as e:
        return HttpResponseServerError('%s' % e.message)
    return HttpResponse(
        r.text, mimetype=r.headers.get('Content-Type', 'text/plain'))


def redirector(request, keyword):
    try:
        url = Url.objects.get(keyword=keyword)
        if url.proxy:
            return _redirect_proxy(url)
        else:
            return HttpResponsePermanentRedirect(url.url)
    except Url.DoesNotExist:
        return HttpResponseNotFound('No URL found for keyword: %s' % keyword)
