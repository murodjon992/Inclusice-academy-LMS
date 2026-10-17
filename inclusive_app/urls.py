from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path

from . import api_views, views

app_name = 'inclusive_app'

# Ommaviy sahifalar: React (Vite) ilovasi boshqaradi. Nomlar saqlangan, shunda admin
# shablonlaridagi {% url 'inclusive_app:...' %} chaqiruvlari ishlashda davom etadi.
spa_routes = [
    path('', views.spa, name='index'),
    path('register/', views.spa, name='register'),
    path('login-user/', views.spa, name='login_user'),
    path('course-test/<int:course_id>/', views.spa, name='course_test'),
    path('test-result/<int:quiz_id>/', views.spa, name='test_result'),
    path('user-dashboard/', views.spa, name='teacher_dashboard'),
    path('user-edit-dashboard/<int:user_id>', views.spa, name='teacher_edit_dashboard'),
    path('dashboard/password/', views.spa, name='password_change'),
    path('yangiliklar/<slug:slug>/', views.spa, name='yangilik_detail'),
    path('course-detail/<slug:slug>/', views.spa, name='course_detail'),
    path('kurslar/', views.spa, name='kurslar'),
    path('videolar/', views.spa, name='videolar'),
    path('testlar/', views.spa, name='testlar'),
    path('test/<int:test_id>', views.spa, name='test_detail'),
    path('evidenve/', views.spa, name='evidenve'),
    path('inclusive/', views.spa, name='inclusive'),
    path('diversity/', views.spa, name='diversity'),
    path('adapting/', views.spa, name='adapting'),
    path('courses/', views.spa, name='courses'),
    path('kurslar/category/<int:cat_id>', views.spa, name='kurslar_category'),
    path('amaliyot/<slug:slug>/', views.spa, name='amaliyot_items'),
    path('amaliyot-list/', views.spa, name='amaliyot_list'),
    path('amaliyotitem-detail/<slug:tur_slug>/<slug:item_slug>', views.spa, name='amaliyotitem_detail_spa'),
    path('kutubxona/', views.spa, name='kutubxona'),
    path('kutubxona-detail/<int:kut_id>', views.spa, name='kutubxona_detail'),
    path('kutubxona/category/<int:cat_id>', views.spa, name='kutubxona_category'),
]

urlpatterns = spa_routes + [
    path("logout/", views.user_logout, name="user_logout"),
    path('kutubxona/file/<int:pk>/', api_views.kutubxona_file_view, name='kutubxona_file_view'),
    path('certificate/<int:course_id>/', api_views.download_certificate, name='download_certificate'),
    # admin panel (React): /manage-admin/ va uning ichki sahifalari
    path('manage-admin/', views.admin_spa, name='admin_dashboard'),
    re_path(r'^manage-admin/.*$', views.admin_spa),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Boshqa hamma manzillar React'ga (u o'zi "Sahifa topilmadi"ni ko'rsatadi). Eng oxirida turishi shart.
urlpatterns += [
    re_path(r'^(?!(?:admin/|api/|static/|media/|manage-admin|logout)).*$', views.spa),
]
