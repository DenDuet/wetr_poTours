from django.urls import path

from . import views

urlpatterns = [
    path("catalog/", views.catalog_dashboard, name="catalog_dashboard"),
    path("catalog/attractions/", views.attractions_list, name="catalog_attractions_list"),
    path("catalog/attractions/create/", views.attraction_create, name="catalog_attraction_create"),
    path("catalog/attractions/<int:pk>/edit/", views.attraction_update, name="catalog_attraction_update"),
    path("catalog/attractions/<int:pk>/archive/", views.attraction_archive, name="catalog_attraction_archive"),
    path("catalog/attractions/<int:pk>/restore/", views.attraction_restore, name="catalog_attraction_restore"),
    path("catalog/includes/", views.includes_list, name="catalog_includes_list"),
    path("catalog/includes/create/", views.include_create, name="catalog_include_create"),
    path("catalog/includes/<int:pk>/edit/", views.include_update, name="catalog_include_update"),
    path("catalog/includes/<int:pk>/archive/", views.include_archive, name="catalog_include_archive"),
    path("catalog/includes/<int:pk>/restore/", views.include_restore, name="catalog_include_restore"),
    path("catalog/tours-days/", views.tours_days_list, name="catalog_tours_days_list"),
    path("catalog/tours-days/create/", views.tours_day_create, name="catalog_tours_day_create"),
    path("catalog/tours-days/<int:pk>/edit/", views.tours_day_update, name="catalog_tours_day_update"),
    path("catalog/tours-days/<int:pk>/archive/", views.tours_day_archive, name="catalog_tours_day_archive"),
    path("catalog/tours-days/<int:pk>/restore/", views.tours_day_restore, name="catalog_tours_day_restore"),
    path("catalog/group-tours/", views.group_tours_list, name="catalog_group_tours_list"),
    path("catalog/group-tours/create/", views.group_tour_create, name="catalog_group_tour_create"),
    path("catalog/group-tours/<int:pk>/edit/", views.group_tour_update, name="catalog_group_tour_update"),
    path("catalog/group-tours/<int:pk>/archive/", views.group_tour_archive, name="catalog_group_tour_archive"),
    path("catalog/group-tours/<int:pk>/restore/", views.group_tour_restore, name="catalog_group_tour_restore"),
    path("catalog/group-tour-media/<int:pk>/delete/", views.group_tour_media_delete, name="catalog_group_tour_media_delete"),
    path("catalog/blog/", views.blog_list, name="catalog_blog_list"),
    path("catalog/blog/create/", views.blog_create, name="catalog_blog_create"),
    path("catalog/blog/<int:pk>/edit/", views.blog_update, name="catalog_blog_update"),
    path("catalog/blog/<int:pk>/archive/", views.blog_archive, name="catalog_blog_archive"),
    path("catalog/blog/<int:pk>/restore/", views.blog_restore, name="catalog_blog_restore"),
]
