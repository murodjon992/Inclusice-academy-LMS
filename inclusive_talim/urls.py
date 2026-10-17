from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inclusive_app.api_urls')),
    path('', include('inclusive_app.urls', namespace='inclusive_app')),
]
