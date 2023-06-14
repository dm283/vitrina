from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('svh_service/', include('svh_service.urls', namespace='svh_service')),
]
