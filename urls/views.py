from __future__ import absolute_import, unicode_literals
from typing import Optional

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html
from django.views.decorators.http import require_POST
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.db import transaction

from .forms import UrlForm
from .models import Url


def _add_event_message(request: HttpRequest, keyword: str, event: str) -> None:
    """
    This methods buids and adds a HTML string to django messages.

    :param request: The current request.
    :param keyword: The keyword causing the event, as a string.
    :param event: The name of the event, as a string (created/deleted/...).
    """
    messages.success(
        request,
        format_html(
            'The keyword <b><a href="{0}" target="_blank">{1}</a>'
            "</b> has been <b>{2}</b> succesfully!",
            reverse("redirector", args=(keyword,)),
            keyword,
            event,
        ),
    )


def list(request: HttpRequest) -> HttpResponse:
    urls = Url.objects.select_related().all()

    if not request.user.is_authenticated:
        urls = urls.filter(public=True)

    return render(
        request,
        "list.html",
        {
            "urls": urls,
            "title": "List",
            "changed_keyword": request.GET.get("changed_keyword"),
            "changed_event_name": request.GET.get("changed_event_name"),
        },
    )


@login_required
@require_POST
@transaction.atomic
def delete(request: HttpRequest, keyword: str) -> HttpResponse:
    url = get_object_or_404(Url, keyword=keyword)
    url.delete()
    _add_event_message(request, keyword, "deleted")
    return redirect("list")


@login_required
@transaction.atomic
def create(request: HttpRequest, keyword: Optional[str] = None):
    if request.method == "POST":
        if keyword is not None:
            # If we're editing, make sure to provide the existing instance.
            form = UrlForm(request.POST, instance=Url.objects.get(keyword=keyword))
        else:
            # Save a new form.
            form = UrlForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.user = request.user
            url.save()

            # If we're changing the keyword of an existing redirect, delete the
            # old one.
            if keyword and keyword != form.cleaned_data["keyword"]:
                Url.objects.filter(keyword=keyword).delete()

            _add_event_message(
                request, url.keyword, "created" if keyword is None else "changed"
            )
            return redirect("list")
    else:
        if keyword is not None:
            form = UrlForm(instance=Url.objects.get(keyword=keyword))
        else:
            form = UrlForm()

    url_name: Optional[str] = getattr(request.resolver_match, "url_name", "")
    if not isinstance(url_name, str) or len(url_name) == 0:
        return HttpResponseNotFound()

    return render(
        request,
        "create.html",
        {
            "form": form,
            "redirect_count": Url.objects.all().count(),
            "title": url_name.title(),
            "keyword": keyword,
        },
    )


def _redirect_proxy(url: str) -> HttpResponse:
    try:
        response: requests.Response = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        return HttpResponseServerError(str(e))
    return HttpResponse(
        response.text, content_type=response.headers.get("Content-Type", "text/plain")
    )


def redirector(_request: HttpRequest, keyword: Optional[str]) -> HttpResponse:
    url: Url = get_object_or_404(Url, keyword=keyword)
    if url.proxy:
        return _redirect_proxy(url.url)
    else:
        return redirect(url.url)
