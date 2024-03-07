from django.urls import path
from . import views

app_name = 'svh_service'

urlpatterns = [
    path('get_app_alive/', views.get_app_alive, name='get_app_alive'),
    path('get_app_stat/', views.get_app_stat, name='get_app_stat'),
]
