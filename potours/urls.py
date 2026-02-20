from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.defaults import page_not_found
from tours import views

handler404 = page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('begin-your-journey/', views.begin_your_journey_step1,
         name='begin_your_journey_step1'),
    path('begin-your-journey/preferences/', views.begin_your_journey_step2,
         name='begin_your_journey_step2'),
    path('begin-your-journey/places/', views.begin_your_journey_step3,
         name='begin_your_journey_step3'),
    path('begin-your-journey/details/', views.begin_your_journey_step4,
         name='begin_your_journey_step4'),
    path('begin-your-journey/thank-you/', views.begin_your_journey_step5,
         name='begin_your_journey_step5'),
    path('group-tours/', views.tours_list, name='tours'),
    path('tours/', views.group_tours_page, name='group_tours_page'),
    path('tours/<int:pk>/', views.tour_detail, name='tour_detail'),
    path('group-tours/<int:pk>/', views.group_tour_detail,
         name='group_tour_detail'),
    path('inspirations/<int:pk>/', views.group_tour_inspiration_detail,
         name='group_tour_inspiration_detail'),
    path('figma-design/', views.figma_design, name='figma_design'),
    path('for-organizations/', views.for_organizations, name='for_organizations'),
    path('about-us/', views.about_us, name='about_us'),
    path('blog/', views.blog_page, name='blog_page'),
    path('blog/<int:pk>/', views.blog_post_detail, name='blog_post_detail'),
    path('attractions/<int:pk>/', views.attraction_detail, name='attraction_detail'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy-policy/', views.page_404_preview, name='privacy_policy'),
    path('', include('tours.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
