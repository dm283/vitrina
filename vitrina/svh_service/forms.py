from django import forms
from .models import Consignment, Contact, Document
from django.contrib.admin.widgets import AdminDateWidget


class ConsignmentForm(forms.ModelForm):
    class Meta:
        model = Consignment
        fields = ['key_id', 'contact', 'contact_name', 'contact_broker', 'broker_name', 'nttn', 'nttn_date',
                  'goods', 'weight', 'dater', 'dateo', 'id_enter', 'car', 'd_in', 'd_out']
        # fields = '__all__'

        widgets = {
            'nttn_date': forms.DateInput(attrs=dict(type='date')),
        }

        labels = {
            'key_id': 'Ключ партии товара', 
            'contact': 'Код клиента', 
            'contact_name': 'Наименование клиента', 
            'contact_broker': 'Код брокера', 
            'broker_name': 'Наименование брокера', 
            'nttn': 'Номер транспортного документа', 
            'nttn_date': 'Дата транспортного документа',
            'goods': 'Номер документа доставки', 
            'weight': 'Вес партии товара', 
            'dater': 'Дата регистрации партии товара', 
            'dateo': 'Дата выдачи партии товара со склада', 
            'id_enter': 'ID пропуска въезда ТС на терминал', 
            'car': 'Номер ТС', 
            'd_in': 'Дата въезда ТС на терминал', 
            'd_out': 'Дата выезда ТС с терминала',
        }

        # help_texts = {
        #     'dater': 'format: yyyy-mm-dd hh:mm:ss',
        #     'dateo': 'format: yyyy-mm-dd hh:mm:ss',
        #     'd_in': 'format: yyyy-mm-dd hh:mm:ss',
        #     'd_out': 'format: yyyy-mm-dd hh:mm:ss',
        # }
        # labels = {
        # }


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        # fields = '__all__'
        fields = ['guid_partia', 'docnum', 'docdate', 'docname', 'file']

        labels = {
            'docnum': 'Номер документа', 
            'docdate': 'Дата документа', 
            'docname': 'Наименование документа', 
            'file': 'Файл', 
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['contact', 'type', 'name', 'inn', 'fio', 'email0', 'email1', 'email2', 'idtelegram', 'tags', 'login', 'pwd', ]
        
        labels = {
            'contact': 'Код клиента', 
            'type': 'Тип пользователя', 
            'name': 'Наименование организации', 
            'inn': 'ИНН организации', 
            'fio': 'ФИО представителя', 
            'email0': 'Почта для смены пароля и контактов по работе портала', 
            'email1': 'Почта отсылки сообщений', 
            'email2': 'Почта для передачи документов партии товара', 
            'idtelegram': 'Telegram ID', 
            'tags': 'Хэштеги', 
            'login': 'Логин', 
            'pwd': 'Пароль', 
        }
