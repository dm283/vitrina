from django.contrib import admin
from .models import Profile, Consignment, Carpass, Contact, Document, Message, Uemail


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'contact', 'type', 'name', ]

@admin.register(Consignment)
class ConsignmentAdmin(admin.ModelAdmin):
    list_display = ['key_id', 'contact_name', 'broker_name', 'dater', 'car', 'datep']

@admin.register(Carpass)
class CarpassAdmin(admin.ModelAdmin):
    list_display = ['id_enter', 'ncar', 'contact_name', 'broker_name', 'dateen', 'timeen']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['contact', 'type', 'name', 'inn', 'fio', 'email1', 'idtelegram', 'f_stop']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['docnum', 'docdate', 'docname', 'f_zip', 'nfile', 'guid_partia']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['guid_partia', 'contact', 'txt', 'datep']

@admin.register(Uemail)
class UemailAdmin(admin.ModelAdmin):
    list_display = ['guid_partia', 'type', 'adrto', 'subj', 'datep']
