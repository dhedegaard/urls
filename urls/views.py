import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseServerError,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from .forms import UrlForm
from .models import Url


def _add_event_message(request: HttpRequest, keyword: str, event: str) -> None:
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


def url_list(request: HttpRequest) -> HttpResponse:
    urls = Url.objects.select_related("user").all()

    if not request.user.is_authenticated:
        urls = urls.filter(public=True)

    return render(
        request,
        "list.html",
        {
            "urls": urls,
            "title": "List",
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
def create(request: HttpRequest, keyword: str | None = None) -> HttpResponse:
    if request.method == "POST":
        if keyword is not None:
            # If we're editing, make sure to provide the existing instance.
            form = UrlForm(
                request.POST, instance=get_object_or_404(Url, keyword=keyword)
            )
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
            form = UrlForm(instance=get_object_or_404(Url, keyword=keyword))
        else:
            form = UrlForm()

    assert request.resolver_match is not None
    assert request.resolver_match.url_name is not None
    return render(
        request,
        "create.html",
        {
            "form": form,
            "redirect_count": Url.objects.all().count(),
            "title": request.resolver_match.url_name.title(),
            "keyword": keyword,
        },
    )


def _redirect_proxy(url: str) -> HttpResponse:
    try:
        response: requests.Response = requests.get(url, timeout=15)
    except requests.exceptions.ConnectionError as e:
        return HttpResponseServerError(str(e))
    return HttpResponse(
        response.text, content_type=response.headers.get("Content-Type", "text/plain")
    )


def redirector(_request: HttpRequest, keyword: str) -> HttpResponse:
    url: Url = get_object_or_404(Url, keyword=keyword)
    if url.proxy:
        return _redirect_proxy(url.url)
    else:
        return redirect(url.url)
