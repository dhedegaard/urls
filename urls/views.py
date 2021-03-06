from __future__ import absolute_import, unicode_literals

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html
from django.views.decorators.http import require_POST
from django.http import (
    HttpResponse,
    HttpResponseServerError,
)
from django.db import transaction

from .forms import UrlForm
from .models import Url


def _add_event_message(request, keyword, event):
    '''
    This methods buids and adds a HTML string to django messages.

    :param request: The current request.
    :param keyword: The keyword causing the event, as a string.
    :param event: The name of the event, as a string (created/deleted/...).
    '''
    messages.success(request, format_html(
        'The keyword <b><a href="{0}" target="_blank">{1}</a>'
        '</b> has been <b>{2}</b> succesfully!',
        reverse('redirector', args=(keyword,)), keyword, event))


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


def list(request):
    urls = Url.objects.select_related().all()

    if not request.user.is_authenticated:
        urls = urls.filter(public=True)

    return render(request, 'list.html', {
        'urls': urls,
        'title': 'List',
        'changed_keyword': request.GET.get('changed_keyword'),
        'changed_event_name': request.GET.get('changed_event_name'),
    })


@login_required
@require_POST
@transaction.atomic
def delete(request, keyword):
    url = get_object_or_404(Url, keyword=keyword)
    url.delete()
    _add_event_message(request, keyword, 'deleted')
    return redirect('list')


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
            # Save a new form.
            form = UrlForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.user = request.user
            url.save()

            # If we're changing the keyword of an existing redirect, delete the
            # old one.
            if keyword and keyword != form.cleaned_data['keyword']:
                Url.objects.filter(keyword=keyword).delete()

            _add_event_message(
                request, url.keyword,
                'created' if keyword is None else 'changed')
            return redirect('list')
    else:
        if keyword is not None:
            form = UrlForm(instance=Url.objects.get(keyword=keyword))
        else:
            form = UrlForm()
    return render(request, 'create.html', {
        'form': form,
        'redirect_count': Url.objects.all().count(),
        'title': request.resolver_match.url_name.title(),
        'keyword': keyword,
    })


def _redirect_proxy(url):
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        return HttpResponseServerError(str(e))
    return HttpResponse(
        r.text, content_type=r.headers.get('Content-Type', 'text/plain'))


def redirector(request, keyword):
    url = get_object_or_404(Url, keyword=keyword)
    if url.proxy:
        return _redirect_proxy(url.url)
    else:
        return redirect(url.url)
