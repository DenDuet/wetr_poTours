# pylint: disable=no-member
import os
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from .forms import AttractionForm, BlogPostForm, GroupTourForm, IncludeForm, ToursDayForm
from .models import (
    Attraction,
    BlogPost,
    GroupTour,
    GroupTourDay,
    GroupTourMedia,
    Include,
    ToursDay,
    ToursDayAttraction,
    ToursDayInclude,
)


def logout_view(request):
    """Выход по GET (по клику на ссылку) с редиректом на главную."""
    logout(request)
    return redirect("home")


def _build_group_tour_cards(queryset, limit=None):
    cards = []
    for group_tour in queryset:
        tour_days = list(group_tour.tour_days.all())
        cities_count = len({d.city.strip().lower()
                           for d in tour_days if d.city})
        image_media = next((m for m in group_tour.media_items.all(
        ) if m.media_type == GroupTourMedia.IMAGE), None)
        cover_url = image_media.file.url if image_media else f"{settings.MEDIA_URL}working/test1/I965-5797-449-1298-368-149.png"
        cards.append(
            {
                "id": group_tour.pk,
                "title": group_tour.title,
                "short_description": group_tour.short_description,
                "tour_days_count": len(tour_days),
                "cities_count": cities_count,
                "cover_url": cover_url,
            }
        )
        if limit and len(cards) >= limit:
            break
    return cards


def _group_tour_card_rows(cards):
    rows = []
    pattern = [2, 3]
    size_idx = 0
    cursor = 0

    while cursor < len(cards):
        row_size = pattern[size_idx % len(pattern)]
        rows.append(
            {
                "size": row_size,
                "cards": cards[cursor:cursor + row_size],
            }
        )
        cursor += row_size
        size_idx += 1

    return rows


def home(request):
    attractions = _attractions_payload()

    featured_qs = (
        GroupTour.objects.order_by("?")
        .prefetch_related("tour_days", "media_items")[:4]
    )
    featured_cards = _build_group_tour_cards(featured_qs, limit=4)
    return render(
        request,
        "index.html",
        {
            "featured_group_tours": featured_cards,
            "featured_attractions": attractions,
        },
    )


def attraction_detail(request, pk):
    """Страница достопримечательности (по образцу blog/13/) с переключением prev/next."""
    attraction = get_object_or_404(Attraction, pk=pk)
    ordered = list(Attraction.objects.order_by("title").values_list("pk", flat=True))
    try:
        idx = ordered.index(attraction.pk)
    except ValueError:
        idx = 0
    prev_pk = ordered[idx - 1] if idx > 0 else None
    next_pk = ordered[idx + 1] if idx < len(ordered) - 1 else None
    return render(
        request,
        "attraction_detail.html",
        {"attraction": attraction, "prev_attraction_pk": prev_pk, "next_attraction_pk": next_pk},
    )


def tours_list(request):
    tours_qs = GroupTour.objects.order_by("-created_at").prefetch_related(
        "tour_days", "media_items"
    )
    cards = _build_group_tour_cards(tours_qs)
    return render(request, "tours.html", {"cards": cards})


def tour_detail(request, pk):
    return render(request, 'tour_detail.html', {'tour_id': pk})


def figma_design(request):
    """Отдельная страница из Figma Make (конвертирована из TSX в HTML/CSS)."""
    return render(request, 'figma-design.html')


def about_us(request):
    """Страница «About Us» — по макету Figma node 989:11673."""
    return render(request, "about_us.html")


def for_organizations(request):
    """Страница «For organizations» — туры для организаций (первая часть макета)."""
    if request.method == "POST" and request.POST.get("submit_request"):
        return redirect(reverse("for_organizations") + "?submitted=1#request-group-tour")
    submitted = request.GET.get("submitted") == "1"
    return render(request, "for_organizations.html", {"submitted": submitted})


def begin_your_journey_step1(request):
    return render(request, "begin_journey_step1.html")


def _attractions_payload():
    attractions = []
    for attraction in Attraction.objects.order_by("title"):
        photo_url = (
            attraction.photo.url
            if attraction.photo
            else f"{settings.MEDIA_URL}working/test1/origOf1icon.jpg"
        )
        attractions.append(
            {
                "id": attraction.pk,
                "title": attraction.title,
                "description": attraction.description,
                "photo_url": photo_url,
                "city": attraction.city,
                "address": attraction.address,
                "duration_hours": str(attraction.duration_hours),
            }
        )
    return attractions


def _attraction_category(attraction):
    text = f"{attraction.title} {attraction.description} {attraction.city}".lower()
    nature_words = ("beach", "mountain", "lake", "park", "forest", "nature")
    city_words = ("city", "square", "center", "old town")
    if any(word in text for word in nature_words):
        return "nature"
    if any(word in text for word in city_words):
        return "city"
    return "historical"


def begin_your_journey_step2(request):
    stage = request.GET.get("stage", "preferences")
    if stage not in {"preferences", "places", "details"}:
        stage = "preferences"

    attractions = _attractions_payload()
    fallback = {
        "title": "North-South Poland Tour",
        "description": "From Historic Cities to Mountain Peaks",
        "photo_url": f"{settings.MEDIA_URL}working/tours/mountains-iceland.png",
    }
    current = attractions[0] if attractions else fallback

    return render(
        request,
        "begin_journey_step2.html",
        {
            "step_stage": stage,
            "slider_current": current,
            "slider_items": attractions if attractions else [fallback],
        },
    )


def begin_your_journey_step3(request):
    attractions_data = []
    for attraction in Attraction.objects.order_by("title"):
        photo_url = (
            attraction.photo.url
            if attraction.photo
            else f"{settings.MEDIA_URL}working/test1/origOf1icon.jpg"
        )
        attractions_data.append(
            {
                "id": attraction.pk,
                "title": attraction.title,
                "description": attraction.description,
                "city": attraction.city,
                "address": attraction.address,
                "duration_hours": str(attraction.duration_hours),
                "photo_url": photo_url,
                "category": _attraction_category(attraction),
            }
        )

    return render(
        request,
        "begin_journey_step3.html",
        {
            "attractions": attractions_data,
            "yandex_maps_api_key": getattr(settings, "YANDEX_MAPS_API_KEY", ""),
        },
    )


def begin_your_journey_step4(request):
    attractions = Attraction.objects.order_by("title")
    cover_attraction = next(
        (a for a in attractions if "malbork" in a.title.lower()),
        attractions.first(),
    )
    cover_url = (
        cover_attraction.photo.url
        if cover_attraction and cover_attraction.photo
        else f"{settings.MEDIA_URL}working/tours/mountains-iceland.png"
    )
    city_choices = sorted(
        {a.city.strip() for a in attractions if a.city and a.city.strip()}
    )
    return render(
        request,
        "begin_journey_step4.html",
        {
            "cover_url": cover_url,
            "city_choices": city_choices,
        },
    )


def begin_your_journey_step5(request):
    attractions = Attraction.objects.order_by("title")
    cover_attraction = next(
        (a for a in attractions if "gdansk" in a.title.lower()
         or "malbork" in a.title.lower()),
        attractions.first(),
    )
    cover_url = (
        cover_attraction.photo.url
        if cover_attraction and cover_attraction.photo
        else f"{settings.MEDIA_URL}working/tours/mountains-iceland.png"
    )
    return render(request, "begin_journey_step5.html", {"cover_url": cover_url})


def group_tours_page(request):
    tours_qs = GroupTour.all_objects.order_by(
        "-created_at").prefetch_related("tour_days", "media_items")
    cards = _build_group_tour_cards(tours_qs)
    context = {
        "group_tour_rows": _group_tour_card_rows(cards),
    }
    return render(request, "group_tours.html", context)


def _group_tour_detail_context(group_tour):
    media_items = list(group_tour.media_items.all())
    image_media = [m for m in media_items if m.media_type ==
                   GroupTourMedia.IMAGE]
    gallery = [m.file.url for m in image_media]
    if not gallery:
        gallery = [f"{settings.MEDIA_URL}working/test1/I965-5797-449-1298-368-149.png"]

    day_links = (
        GroupTourDay.objects.filter(group_tour=group_tour)
        .select_related("tours_day")
        .order_by("day_number")
    )
    itinerary = []
    cities = set()
    highlights = []
    seen_highlights = set()
    tour_includes = []
    seen_includes = set()
    for link in day_links:
        day = link.tours_day
        if day.city:
            cities.add(day.city.strip().lower())
        for include in day.includes.all():
            if include.pk not in seen_includes:
                tour_includes.append(include)
                seen_includes.add(include.pk)
        day_attractions = []
        for attraction in day.attractions.all():
            day_attractions.append(
                {
                    "title": attraction.title,
                    "city": attraction.city,
                    "duration_hours": attraction.duration_hours,
                    "photo_url": attraction.photo.url if attraction.photo else (day.photo.url if day.photo else gallery[0]),
                }
            )
            if attraction.pk not in seen_highlights and len(highlights) < 6:
                highlights.append(day_attractions[-1])
                seen_highlights.add(attraction.pk)
        itinerary.append(
            {
                "day_number": link.day_number,
                "title": day.title,
                "description": day.description,
                "city": day.city,
                "duration_hours": day.duration_hours,
                "photo_url": day.photo.url if day.photo else gallery[0],
                "attractions": day_attractions,
            }
        )

    return {
        "group_tour": group_tour,
        "gallery": gallery,
        "cover_url": gallery[0],
        "tour_days_count": len(itinerary),
        "cities_count": len(cities),
        "group_size": group_tour.group_size,
        "rating": "4.8/5",
        "itinerary": itinerary,
        "highlights": highlights,
        "tour_includes": tour_includes,
    }


def group_tour_detail(request, pk):
    group_tour = get_object_or_404(
        GroupTour.objects.prefetch_related(
            "media_items",
            "tour_days__attractions",
            "tour_days__includes",
        ),
        pk=pk,
    )
    context = _group_tour_detail_context(group_tour)
    # Иконки includes берём из media/working/icons/
    includes_with_icons_path = []
    for inc in context["tour_includes"]:
        icon_url = ""
        if inc.icon_path:
            icon_url = f"{settings.MEDIA_URL}working/icons/{os.path.basename(inc.icon_path)}"
        includes_with_icons_path.append({
            "description": inc.description,
            "icon_path": inc.icon_path,
            "icon_url": icon_url,
        })
    context["tour_includes"] = includes_with_icons_path
    return render(request, "group_tour_detail.html", context)


def group_tour_inspiration_detail(request, pk):
    group_tour = get_object_or_404(
        GroupTour.objects.prefetch_related(
            "media_items",
            "tour_days__attractions",
            "tour_days__includes",
        ),
        pk=pk,
    )
    context = _group_tour_detail_context(group_tour)
    # Иконки includes на странице inspirations берём из media/working/icons/
    includes_with_icons_path = []
    for inc in context["tour_includes"]:
        icon_url = ""
        if inc.icon_path:
            icon_url = f"{settings.MEDIA_URL}working/icons/{os.path.basename(inc.icon_path)}"
        includes_with_icons_path.append({
            "description": inc.description,
            "icon_path": inc.icon_path,
            "icon_url": icon_url,
        })
    context["tour_includes"] = includes_with_icons_path
    return render(request, "group_tour_inspiration_detail.html", context)


def _creator_or_none(request):
    if request.user.is_authenticated:
        return request.user
    return None


def _save_tours_day_relations(instance, attractions, includes):
    ToursDayAttraction.objects.filter(tours_day=instance).delete()
    for idx, attraction in enumerate(attractions, start=1):
        ToursDayAttraction.objects.create(
            tours_day=instance,
            attraction=attraction,
            position=idx,
        )

    ToursDayInclude.objects.filter(tours_day=instance).delete()
    for idx, include in enumerate(includes, start=1):
        ToursDayInclude.objects.create(
            tours_day=instance,
            include=include,
            position=idx,
        )


def _save_group_tour_days(instance, tour_days):
    GroupTourDay.objects.filter(group_tour=instance).delete()
    for idx, tours_day in enumerate(tour_days, start=1):
        GroupTourDay.objects.create(
            group_tour=instance,
            tours_day=tours_day,
            day_number=idx,
        )


def _save_group_tour_media(instance, files):
    for media_file in files:
        content_type = getattr(media_file, "content_type", "") or ""
        media_type = GroupTourMedia.VIDEO if content_type.startswith(
            "video/") else GroupTourMedia.IMAGE
        GroupTourMedia.objects.create(
            group_tour=instance,
            file=media_file,
            media_type=media_type,
        )


def catalog_dashboard(request):
    context = {
        "attractions_count": Attraction.objects.count(),
        "attractions_archived_count": Attraction.all_objects.filter(is_archived=True).count(),
        "tours_days_count": ToursDay.objects.count(),
        "tours_days_archived_count": ToursDay.all_objects.filter(is_archived=True).count(),
        "includes_count": Include.objects.count(),
        "includes_archived_count": Include.all_objects.filter(is_archived=True).count(),
        "group_tours_count": GroupTour.objects.count(),
        "group_tours_archived_count": GroupTour.all_objects.filter(is_archived=True).count(),
        "blog_posts_count": BlogPost.objects.count(),
        "blog_posts_archived_count": BlogPost.all_objects.filter(is_archived=True).count(),
    }
    return render(request, "catalog/dashboard.html", context)


def attractions_list(request):
    context = {
        "items": Attraction.objects.order_by("title"),
        "archived_items": Attraction.all_objects.filter(is_archived=True).order_by("title"),
    }
    return render(request, "catalog/attractions/list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def attraction_create(request):
    form = AttractionForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        attraction = form.save(commit=False)
        attraction.user = _creator_or_none(request)
        attraction.save()
        messages.success(request, "Attraction created.")
        return redirect("catalog_attractions_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Create attraction"})


@login_required
@require_http_methods(["GET", "POST"])
def attraction_update(request, pk):
    attraction = get_object_or_404(Attraction.all_objects, pk=pk)
    form = AttractionForm(request.POST or None,
                          request.FILES or None, instance=attraction)
    if request.method == "POST" and form.is_valid():
        attraction = form.save(commit=False)
        if not attraction.user:
            attraction.user = _creator_or_none(request)
        attraction.save()
        messages.success(request, "Attraction updated.")
        return redirect("catalog_attractions_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Edit attraction"})


@login_required
@require_POST
def attraction_archive(request, pk):
    attraction = get_object_or_404(Attraction, pk=pk)
    attraction.archive()
    messages.success(request, "Attraction moved to archive.")
    return redirect("catalog_attractions_list")


@login_required
@require_POST
def attraction_restore(request, pk):
    attraction = get_object_or_404(Attraction.all_objects, pk=pk)
    attraction.restore()
    messages.success(request, "Attraction restored.")
    return redirect("catalog_attractions_list")


def includes_list(request):
    context = {
        "items": Include.objects.order_by("description"),
        "archived_items": Include.all_objects.filter(is_archived=True).order_by("description"),
    }
    return render(request, "catalog/includes/list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def include_create(request):
    form = IncludeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Include created.")
        return redirect("catalog_includes_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Create include"})


@login_required
@require_http_methods(["GET", "POST"])
def include_update(request, pk):
    include = get_object_or_404(Include.all_objects, pk=pk)
    form = IncludeForm(request.POST or None, instance=include)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Include updated.")
        return redirect("catalog_includes_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Edit include"})


@login_required
@require_POST
def include_archive(request, pk):
    include = get_object_or_404(Include, pk=pk)
    include.archive()
    messages.success(request, "Include moved to archive.")
    return redirect("catalog_includes_list")


@login_required
@require_POST
def include_restore(request, pk):
    include = get_object_or_404(Include.all_objects, pk=pk)
    include.restore()
    messages.success(request, "Include restored.")
    return redirect("catalog_includes_list")


def tours_days_list(request):
    context = {
        "items": ToursDay.objects.order_by("title"),
        "archived_items": ToursDay.all_objects.filter(is_archived=True).order_by("title"),
    }
    return render(request, "catalog/tours_days/list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def tours_day_create(request):
    form = ToursDayForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        tours_day = form.save(commit=False)
        tours_day.user = _creator_or_none(request)
        tours_day.save()
        _save_tours_day_relations(
            instance=tours_day,
            attractions=form.cleaned_data["attractions"],
            includes=form.cleaned_data["includes"],
        )
        messages.success(request, "Tour day created.")
        return redirect("catalog_tours_days_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Create tour day"})


@login_required
@require_http_methods(["GET", "POST"])
def tours_day_update(request, pk):
    tours_day = get_object_or_404(ToursDay.all_objects, pk=pk)
    form = ToursDayForm(request.POST or None,
                        request.FILES or None, instance=tours_day)
    if request.method == "POST" and form.is_valid():
        tours_day = form.save(commit=False)
        if not tours_day.user:
            tours_day.user = _creator_or_none(request)
        tours_day.save()
        _save_tours_day_relations(
            instance=tours_day,
            attractions=form.cleaned_data["attractions"],
            includes=form.cleaned_data["includes"],
        )
        messages.success(request, "Tour day updated.")
        return redirect("catalog_tours_days_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Edit tour day"})


@login_required
@require_POST
def tours_day_archive(request, pk):
    tours_day = get_object_or_404(ToursDay, pk=pk)
    tours_day.archive()
    messages.success(request, "Tour day moved to archive.")
    return redirect("catalog_tours_days_list")


@login_required
@require_POST
def tours_day_restore(request, pk):
    tours_day = get_object_or_404(ToursDay.all_objects, pk=pk)
    tours_day.restore()
    messages.success(request, "Tour day restored.")
    return redirect("catalog_tours_days_list")


def group_tours_list(request):
    context = {
        "items": GroupTour.objects.order_by("title").prefetch_related("media_items"),
        "archived_items": GroupTour.all_objects.filter(is_archived=True).order_by("title"),
    }
    return render(request, "catalog/group_tours/list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def group_tour_create(request):
    form = GroupTourForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        group_tour = form.save(commit=False)
        group_tour.user = _creator_or_none(request)
        group_tour.save()
        _save_group_tour_days(group_tour, form.cleaned_data["tour_days"])
        _save_group_tour_media(
            group_tour, request.FILES.getlist("media_files"))
        messages.success(request, "Group tour created.")
        return redirect("catalog_group_tours_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Create group tour"})


@login_required
@require_http_methods(["GET", "POST"])
def group_tour_update(request, pk):
    group_tour = get_object_or_404(
        GroupTour.all_objects.prefetch_related("media_items"), pk=pk)
    form = GroupTourForm(request.POST or None,
                         request.FILES or None, instance=group_tour)
    if request.method == "POST" and form.is_valid():
        group_tour = form.save(commit=False)
        if not group_tour.user:
            group_tour.user = _creator_or_none(request)
        group_tour.save()
        _save_group_tour_days(group_tour, form.cleaned_data["tour_days"])
        _save_group_tour_media(
            group_tour, request.FILES.getlist("media_files"))
        messages.success(request, "Group tour updated.")
        return redirect("catalog_group_tours_list")
    return render(
        request,
        "catalog/form_page.html",
        {
            "form": form,
            "title": "Edit group tour",
            "existing_media": group_tour.media_items.all(),
        },
    )


@login_required
@require_POST
def group_tour_archive(request, pk):
    group_tour = get_object_or_404(GroupTour, pk=pk)
    group_tour.archive()
    messages.success(request, "Group tour moved to archive.")
    return redirect("catalog_group_tours_list")


@login_required
@require_POST
def group_tour_restore(request, pk):
    group_tour = get_object_or_404(GroupTour.all_objects, pk=pk)
    group_tour.restore()
    messages.success(request, "Group tour restored.")
    return redirect("catalog_group_tours_list")


@login_required
@require_POST
def group_tour_media_delete(request, pk):
    media = get_object_or_404(GroupTourMedia, pk=pk)
    group_tour_id = media.group_tour_id
    media.delete()
    messages.success(request, "Media deleted.")
    return redirect("catalog_group_tour_update", pk=group_tour_id)


# ——— Блог (каталог) ———
def _blog_list_queryset(request, base_queryset):
    qs = base_queryset
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    search = request.GET.get("search", "").strip()
    if date_from:
        try:
            d = datetime.strptime(date_from, "%Y-%m-%d").date()
            qs = qs.filter(published_at__gte=d)
        except ValueError:
            pass
    if date_to:
        try:
            d = datetime.strptime(date_to, "%Y-%m-%d").date()
            qs = qs.filter(published_at__lte=d)
        except ValueError:
            pass
    if search:
        qs = qs.filter(
            Q(title__icontains=search) | Q(body__icontains=search)
        )
    sort = request.GET.get("sort", "date")
    order = request.GET.get("order", "desc")
    if order not in ("asc", "desc"):
        order = "desc"
    order_prefix = "" if order == "asc" else "-"
    sort_map = {"title": "title", "date": "published_at", "author": "user__username"}
    order_field = sort_map.get(sort, "published_at")
    qs = qs.order_by(f"{order_prefix}{order_field}", "-created_at")
    return qs, {"sort": sort, "order": order, "date_from": date_from, "date_to": date_to, "search": search}


def blog_list(request):
    active = BlogPost.objects.all()
    archived = BlogPost.all_objects.filter(is_archived=True)
    items, params = _blog_list_queryset(request, active)
    archived_items, _ = _blog_list_queryset(request, archived)
    context = {
        "items": items,
        "archived_items": archived_items,
        "sort": params["sort"],
        "order": params["order"],
        "date_from": params["date_from"],
        "date_to": params["date_to"],
        "search": params["search"],
    }
    return render(request, "catalog/blog/list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def blog_create(request):
    form = BlogPostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.user = _creator_or_none(request)
        post.save()
        messages.success(request, "Blog post created.")
        return redirect("catalog_blog_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Create blog post"})


@login_required
@require_http_methods(["GET", "POST"])
def blog_update(request, pk):
    post = get_object_or_404(BlogPost.all_objects, pk=pk)
    form = BlogPostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        if not post.user:
            post.user = _creator_or_none(request)
        post.save()
        messages.success(request, "Blog post updated.")
        return redirect("catalog_blog_list")
    return render(request, "catalog/form_page.html", {"form": form, "title": "Edit blog post"})


@login_required
@require_POST
def blog_archive(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.archive()
    messages.success(request, "Blog post moved to archive.")
    return redirect("catalog_blog_list")


@login_required
@require_POST
def blog_restore(request, pk):
    post = get_object_or_404(BlogPost.all_objects, pk=pk)
    post.restore()
    messages.success(request, "Blog post restored.")
    return redirect("catalog_blog_list")


# ——— Публичная страница Our Blog ———
def blog_page(request):
    qs = BlogPost.objects.order_by("-published_at", "-created_at")
    paginator = Paginator(qs, 9)
    try:
        page_number = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        page_number = 1
    page = paginator.get_page(page_number)
    return render(
        request,
        "blog.html",
        {
            "page_obj": page,
            "posts": page.object_list,
        },
    )


def blog_post_detail(request, pk):
    post = get_object_or_404(BlogPost.objects, pk=pk)
    return render(
        request,
        "blog_post_detail.html",
        {"post": post},
    )


def page_404_preview(request):
    """Показывает кастомную страницу 404."""
    return render(request, "404.html")


def terms_and_conditions(request):
    """Страница Terms and Conditions."""
    return render(request, "terms_and_conditions.html")
