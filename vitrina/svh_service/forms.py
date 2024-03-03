import sys, os, configparser
from django import forms
from .models import Consignment, Carpass, Contact, Document, TYPE_CHOICES
from django.shortcuts import get_object_or_404
from pathlib import Path


config = configparser.ConfigParser()
config_file = os.path.join(Path(__file__).resolve().parent.parent, 'vitrina', 'config.ini')
if os.path.exists(config_file):
    config.read(config_file, encoding='utf-8')
else:
    print("error! config file doesn't exist"); sys.exit()

APP_TYPE = config['app']['app_type']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    

class ConsignmentForm(forms.ModelForm):
    class Meta:
        model = Consignment
        if APP_TYPE == 'operator':
            is_ro = False
        elif APP_TYPE == 'client':
            is_ro = True

        fields = ['key_id', 'contact_name', 'contact', 'broker_name', 'contact_broker', 'nttn', 'nttn_date',
                  'dkd', 'dkd_date', 'goods', 'weight', 'dater', 'dateo', 'id_enter', 'car', 'd_in', 'd_out']

        widgets = {
            'key_id': forms.HiddenInput(),
            'nttn_date': forms.DateInput(attrs=dict(type='date', readonly=is_ro)),
            'dkd_date': forms.DateInput(attrs=dict(type='date', readonly=is_ro)),
            'dater': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}),
            'dateo': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}),
            'd_in': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}), 
            'd_out': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}),
            'contact': forms.HiddenInput(),
            'contact_broker': forms.HiddenInput(),
            'contact_name': forms.TextInput(attrs={'readonly': is_ro}),
            'broker_name': forms.TextInput(attrs={'readonly': is_ro}),
            'nttn': forms.TextInput(attrs={'readonly': is_ro}),
            'dkd': forms.TextInput(attrs={'readonly': is_ro}),
            'goods': forms.TextInput(attrs={'readonly': is_ro}),
            'weight': forms.TextInput(attrs={'readonly': is_ro}),
            'id_enter': forms.TextInput(attrs={'readonly': is_ro}),
            'car': forms.TextInput(attrs={'readonly': is_ro}),
        }

        labels = {
            'key_id': 'ID партии товара', 
            'contact': 'Код клиента', 
            'contact_name': 'Наименование клиента', 
            'contact_broker': 'Код брокера', 
            'broker_name': 'Наименование брокера', 
            'nttn': '№ транспортного документа', 
            'nttn_date': 'Дата транспортного документа',
            'dkd': '№ документа доставки',
            'dkd_date': 'Дата документа доставки',
            'goods': 'Описание товаров', 
            'weight': 'Вес партии товара', 
            'dater': 'Дата регистрации партии товара', 
            'dateo': 'Дата выдачи партии товара со склада', 
            'id_enter': 'ID пропуска въезда ТС на терминал', 
            'car': 'Номер ТС', 
            'd_in': 'Дата въезда ТС на терминал', 
            'd_out': 'Дата выезда ТС с терминала',
        }


class ConsignmentPostedForm(ConsignmentForm):
    class Meta(ConsignmentForm.Meta):
        is_ro = True
        widgets = {
            'key_id': forms.HiddenInput(),
            'nttn_date': forms.DateInput(attrs=dict(type='date', readonly=is_ro)),
            'dkd_date': forms.DateInput(attrs=dict(type='date', readonly=is_ro)),
            'dater': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}),
            'dateo': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}),
            'd_in': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}), 
            'd_out': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}),
            'contact': forms.HiddenInput(),
            'contact_broker': forms.HiddenInput(),
            'contact_name': forms.TextInput(attrs={'readonly': is_ro}),
            'broker_name': forms.TextInput(attrs={'readonly': is_ro}),
            'nttn': forms.TextInput(attrs={'readonly': is_ro}),
            'dkd': forms.TextInput(attrs={'readonly': is_ro}),
            'goods': forms.TextInput(attrs={'readonly': is_ro}),
            'weight': forms.TextInput(attrs={'readonly': is_ro}),
            'id_enter': forms.TextInput(attrs={'readonly': is_ro}),
            'car': forms.TextInput(attrs={'readonly': is_ro}),
        }


class ConsignmentFiltersForm(forms.Form):
    key_id = forms.CharField(label='ID партии', max_length=16, required=False)
    contact_name = forms.CharField(label='Клиент', max_length=150, required=False)
    broker_name = forms.CharField(label='Брокер', max_length=150, required=False)
    dater_from = forms.DateField(label='Дата регистрации, c', widget=forms.DateInput(attrs=dict(type='date')), required=False)
    dater_to = forms.DateField(label='по', widget=forms.DateInput(attrs=dict(type='date')), required=False)
    nttn =  forms.CharField(label='№ транспортного документа', max_length=100, required=False)
    dateo_from = forms.DateField(label='Дата выдачи, с', widget=forms.DateInput(attrs=dict(type='date')), required=False)
    dateo_to = forms.DateField(label='по', widget=forms.DateInput(attrs=dict(type='date')), required=False)
    dkd = forms.CharField(label='№ документа доставки', max_length=100, required=False)
    car = forms.CharField(label='ТС', max_length=30, required=False)
    on_terminal = forms.BooleanField(label='На складе', widget=forms.CheckboxInput(), initial=False, required=False)


class CarpassFiltersForm(forms.Form):
    id_enter = forms.CharField(label='ID пропуска', max_length=8, required=False)
    dateen_from = forms.DateField(label='Дата въезда, с', widget=forms.DateInput(attrs=dict(type='date')), required=False)
    dateen_to = forms.DateField(label='Дата въезда, по', widget=forms.DateInput(attrs=dict(type='date')), required=False)
    ncar = forms.CharField(label='ТС', max_length=255, required=False)
    ntir = forms.CharField(label='№ документа доставки', max_length=50, required=False)
    nkont = forms.CharField(label='№ контейнера', max_length=50, required=False)


class ContactFiltersForm(forms.Form):
    TYPE_CHOICES += (('', 'любой'),)
    contact = forms.IntegerField(label='Код клиента', required=False) # Код клиента из программы Альта-СВХ
    type = forms.ChoiceField(label='Тип', choices=TYPE_CHOICES, initial='', required=False) # Тип пользователя
    name = forms.CharField(label='Организация', max_length=150, required=False) # Наименование организации
    inn = forms.CharField(label='ИНН', max_length=12, required=False) # ИНН организации
    email1 = forms.CharField(label='E-mail', max_length=100, required=False) # Почта отсылки сообщений
    idtelegram = forms.CharField(label='Telegram ID', max_length=36, required=False) # Идентификатор ID messenger Telegram


class CarpassForm(forms.ModelForm):
    class Meta:
        model = Carpass
        if APP_TYPE == 'operator':
            is_ro = False
        elif APP_TYPE == 'client':
            is_ro = True

        fields = ['guid', 'id_enter', 'ncar', 'dateen', 'timeen', 'ntir', 'nkont',
                  'driver', 'drv_man', 'dev_phone', 'contact_name', 'contact', 'broker_name', 'contact_broker', 
                  'place_n', 'dateex', 'timeex']

        widgets = {
            'guid': forms.HiddenInput(),
            'id_enter': forms.HiddenInput(),
            'dateen': forms.DateInput(attrs=dict(type='date', readonly=is_ro)),
            'dateex': forms.DateInput(attrs=dict(type='date', readonly=is_ro)),
            'timeen': forms.TimeInput(attrs={'type': 'time', 'readonly': is_ro}),
            'timeex': forms.TimeInput(attrs={'type': 'time', 'readonly': is_ro}),
            # 'contact': forms.TextInput(attrs={'readonly': True, 'readonly': True}),
            # 'contact_broker': forms.TextInput(attrs={'readonly': True, 'readonly': True}),
            'contact': forms.HiddenInput(),
            'contact_broker': forms.HiddenInput(),
            'ncar': forms.TextInput(attrs={'readonly': is_ro}),
            'ntir': forms.TextInput(attrs={'readonly': is_ro}),
            'nkont': forms.TextInput(attrs={'readonly': is_ro}),
            'driver': forms.TextInput(attrs={'readonly': is_ro}),
            'drv_man': forms.TextInput(attrs={'readonly': is_ro}),
            'dev_phone': forms.TextInput(attrs={'readonly': is_ro}),
            'place_n': forms.TextInput(attrs={'readonly': is_ro}),
            'contact_name': forms.TextInput(attrs={'readonly': is_ro}),
            'broker_name': forms.TextInput(attrs={'readonly': is_ro}),
        }

        labels = {
            # 'guid': 'Уникальный идентификатор записи', 
            # 'id_enter': 'ID пропуска въезда ТС на терминал', 
            'ncar': 'Номер ТС', 
            'dateen': 'Дата въезда', 
            'timeen': 'Время въезда', 
            'ntir': 'Номер документа доставки', 
            'nkont': 'Номер контейнера', 
            'driver': 'Наименование перевозчика', 
            'drv_man': 'ФИО водителя', 
            'dev_phone': 'Телефон водителя для связи', 
            'contact': 'Код клиента', 
            'contact_name': 'Наименование клиента', 
            'contact_broker': 'Код брокера', 
            'broker_name': 'Наименование брокера', 
            'place_n': 'Номер стоянки', 
            'dateex': 'Дата выезда',
            'timeex': 'Время выезда', 
        }


class CarpassPostedForm(CarpassForm):
    class Meta(CarpassForm.Meta):
        is_ro = True
        widgets = {
            'guid': forms.HiddenInput(),
            'id_enter': forms.HiddenInput(),
            'dateen': forms.DateInput(attrs=dict(type='date', readonly=is_ro)),
            'dateex': forms.DateInput(attrs=dict(type='date', readonly=is_ro)),
            'timeen': forms.TimeInput(attrs={'type': 'time', 'readonly': is_ro}),
            'timeex': forms.TimeInput(attrs={'type': 'time', 'readonly': is_ro}),
            # 'contact': forms.TextInput(attrs={'readonly': True, 'readonly': True}),
            # 'contact_broker': forms.TextInput(attrs={'readonly': True, 'readonly': True}),
            'contact': forms.HiddenInput(),
            'contact_broker': forms.HiddenInput(),
            'ncar': forms.TextInput(attrs={'readonly': is_ro}),
            'ntir': forms.TextInput(attrs={'readonly': is_ro}),
            'nkont': forms.TextInput(attrs={'readonly': is_ro}),
            'driver': forms.TextInput(attrs={'readonly': is_ro}),
            'drv_man': forms.TextInput(attrs={'readonly': is_ro}),
            'dev_phone': forms.TextInput(attrs={'readonly': is_ro}),
            'place_n': forms.TextInput(attrs={'readonly': is_ro}),
            'contact_name': forms.TextInput(attrs={'readonly': is_ro}),
            'broker_name': forms.TextInput(attrs={'readonly': is_ro}),
        }


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        # fields = '__all__'
        if APP_TYPE == 'operator':
            fields = ['guid_partia', 'id_enter', 'docnum', 'docdate', 'docname', 'file', 'nfile', ]
            is_ro = False
        elif APP_TYPE == 'client':
            fields = ['guid_partia', 'id_enter', 'docnum', 'docdate', 'docname', 'nfile', ]
            is_ro = True

        widgets = {
            'guid_partia': forms.HiddenInput(),
            'id_enter': forms.HiddenInput(),
            'docnum': forms.TextInput(attrs={'readonly': is_ro}),
            'docdate': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}),
            'docname': forms.TextInput(attrs={'readonly': is_ro}),
            'nfile': forms.TextInput(attrs={'readonly': True}),
            'file': forms.FileInput(),
        }
        # forms.TextInput(attrs={'disabled': 'disabled'})

        labels = {
            'docnum': 'Номер', 
            'docdate': 'Дата', 
            'docname': 'Наименование', 
            'file': 'Загрузка файла',
            'nfile': 'Загруженный файл'
        }


class DocumentPostedForm(DocumentForm):
    class Meta(DocumentForm.Meta):
        is_ro = True
        widgets = {
            'guid_partia': forms.HiddenInput(),
            'id_enter': forms.HiddenInput(),
            'docnum': forms.TextInput(attrs={'readonly': is_ro}),
            'docdate': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': is_ro}),
            'docname': forms.TextInput(attrs={'readonly': is_ro}),
            'nfile': forms.TextInput(attrs={'readonly': True}),
            'file': forms.HiddenInput(),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['contact', 'type', 'name', 'inn', 'fio', 'email0', 'email1', 'email2', 'idtelegram', 'tags', ]
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
        }
        help_texts = {
            'contact': '*', 
            'type': '*', 
            'name': '*', 
            'inn': '*', 
            'fio': '*', 
            'email0': '*', 
            'email1': '*', 
            'email2': '*', 
        }

    def clean(self):
        super(ContactForm, self).clean()
        cd = self.cleaned_data

        if cd['inn'] != '':
            if not cd['inn'].isdigit():
                self._errors['inn'] = self.error_class(['Некорректный формат ИНН'])
            if cd['inn'].isdigit() and len(cd['inn']) < 10:
                self._errors['inn'] = self.error_class(['Некорректный формат ИНН: менее 10 цифр'])
            if cd['inn'].isdigit() and cd['inn'][0] == '0':
                self._errors['inn'] = self.error_class(['Некорректный формат ИНН: не может начинаться с 0'])
    
        return self.cleaned_data


class ContactPostedForm(ContactForm):
    class Meta(ContactForm.Meta):
        is_ro = True
        widgets = {
            'contact': forms.TextInput(attrs={'readonly': is_ro}),
            'type': forms.TextInput(attrs={'readonly': is_ro}),
            'name': forms.TextInput(attrs={'readonly': is_ro}),
            'inn': forms.TextInput(attrs={'readonly': is_ro}),
            'fio': forms.TextInput(attrs={'readonly': is_ro}),
            'email0': forms.TextInput(attrs={'readonly': is_ro}),
            'email1': forms.TextInput(attrs={'readonly': is_ro}),
            'email2': forms.TextInput(attrs={'readonly': is_ro}),
            'idtelegram': forms.TextInput(attrs={'readonly': is_ro}),
            'tags': forms.TextInput(attrs={'readonly': is_ro}),
        
        }

