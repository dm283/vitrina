from django.urls import path
from . import views


app_name = 'svh_service'

urlpatterns = [
    path('consignments', views.consignment_list, name='consignment_list'),
    # path('consignments/<int:id>/', views.consignment_detail, name='consignment_detail'),
    path('consignments/<int:id>/', views.consignment_update, name='consignment_update'),
    path('consignments/add', views.consignment_add, name='consignment_add'),
    path('consignments/add_complete', views.post_consignment, name='post_consignment'),
    path('consignments/<int:id>/update', views.consignment_update, name='consignment_update'),
    path('consignments/<int:id>/delete', views.consignment_delete, name='consignment_delete'),
    path('consignments/<int:id>/post', views.consignment_post, name='consignment_post'),
    path('consignments/<int:id>/rollback', views.consignment_rollback, name='consignment_rollback'),
    path('consignments/<int:id>/close', views.consignment_close, name='consignment_close'),
    path('consignments/<int:id>/add_document', views.consignment_add_document, name='consignment_add_document'),

    path('documents/<int:id>/update', views.document_update, name='document_update'),
    path('documents/<int:id>/delete', views.document_delete, name='document_delete'),
    path('documents/<int:id>/close', views.document_close, name='document_close'),

    path('contacts', views.contact_list, name='contact_list'),
    path('contacts/<int:id>/', views.contact_update, name='contact_update'),
    path('contacts/add', views.contact_add, name='contact_add'),
    path('contacts/add_complete', views.post_contact, name='post_contact'),
    path('contacts/<int:id>/update', views.contact_update, name='contact_update'),
    path('contacts/<int:id>/delete', views.contact_delete, name='contact_delete'),
    path('contacts/<int:id>/post', views.contact_post, name='contact_post'),
    path('contacts/<int:id>/rollback', views.contact_rollback, name='contact_rollback'),
    path('contacts/<int:id>/close', views.contact_close, name='contact_close'),
]
