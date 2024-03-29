from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


app_name = 'svh_service'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('consignments', views.consignment_list, name='consignment_list'),
    path('consignments/<int:id>/', views.consignment_update, name='consignment_update'),
    path('consignments/<int:id>/update', views.consignment_update, name='consignment_update'),
    path('consignments/<int:id>/delete', views.consignment_delete, name='consignment_delete'),
    path('consignments/<int:id>/post', views.consignment_post, name='consignment_post'),
    path('consignments/<int:id>/rollback', views.consignment_rollback, name='consignment_rollback'),
    path('consignments/<int:id>/close', views.consignment_close, name='consignment_close'),

    path('<str:entity_type>/object_add', views.object_add, name='object_add'),   #########

    path('erase_filters/<str:entity>/', views.erase_filters, name='erase_filters'),

    path('carpass', views.carpass_list, name='carpass_list'),
    path('carpass/<int:id>/', views.carpass_update, name='carpass_update'),
    path('carpass/<int:id>/update', views.carpass_update, name='carpass_update'),
    path('carpass/<int:id>/delete', views.carpass_delete, name='carpass_delete'),
    path('carpass/<int:id>/post', views.carpass_post, name='carpass_post'),
    path('carpass/<int:id>/rollback', views.carpass_rollback, name='carpass_rollback'),
    path('carpass/<int:id>/close', views.carpass_close, name='carpass_close'),

    path('documents/<str:entity_type>/<int:entity_id>/add_document', views.document_add, name='document_add'),
    path('documents/<int:id>/update', views.document_update, name='document_update'),
    path('documents/<int:id>/delete', views.document_delete, name='document_delete'),
    path('documents/<int:id>/close', views.document_close, name='document_close'),
    path('documents/<int:id>/download', views.document_download, name='document_download'),

    path('contacts', views.contact_list, name='contact_list'),
    path('contacts/<int:id>/', views.contact_update, name='contact_update'),
    path('contacts/<int:id>/update', views.contact_update, name='contact_update'),
    path('contacts/<int:id>/delete', views.contact_delete, name='contact_delete'),
    path('contacts/<int:id>/post', views.contact_post, name='contact_post'),
    path('contacts/<int:id>/rollback', views.contact_rollback, name='contact_rollback'),
    path('contacts/<int:id>/close', views.contact_close, name='contact_close'),
]
