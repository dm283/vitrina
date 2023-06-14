from django.db import models


class Consignment(models.Model):
    key_id = models.CharField(max_length=16, unique=True) # Ключ партии товара в Альта-СВХ. 
    contact = models.IntegerField(blank=True, null=True) # Код клиента 
    contact_name = models.CharField(max_length=150, blank=True, default='') # Наименование клиента
    contact_broker = models.IntegerField(blank=True, null=True) # Код брокера оформляющего товар
    broker_name = models.CharField(max_length=150, blank=True,  default='') # Наименование брокера
    nttn = models.CharField(max_length=100, blank=True, default='') # Номер транспортного документа
    nttn_date = models.DateField(blank=True, null=True) # Дата транспортного документа
    goods = models.CharField(max_length=100, blank=True, default='') # Номер документа доставки
    weight = models.FloatField(default=0) # Вес партии товара
    dater = models.DateTimeField(blank=True, null=True) # Дата регистрации партии товара
    dateo = models.DateTimeField(blank=True, null=True) # Дата выдачи партии товара со склада
    id_enter = models.CharField(max_length=8, blank=True, default='') # Id пропуска въезда транпортного средства на терминал
    car =  models.CharField(max_length=20, blank=True, default='') # Номер транспортного средства 
    d_in = models.DateTimeField(blank=True, null=True) # Дата въезда транспортного средства на терминал
    d_out = models.DateTimeField(blank=True, null=True) # Дата выезда транспортного средства с терминала 
    guid_user = models.CharField(max_length=36, blank=True, default='') # GUID пользователя который создал эту запись
    datep = models.DateTimeField(auto_now_add=True) # Дата создания записи
    posted = models.BooleanField(default=False) # флаг проводки
    post_date = models.DateTimeField(blank=True, null=True) # дата проводки
    post_user_id = models.CharField(max_length=36, blank=True, default='') # идентификатор пользователя  который провел запись
    was_posted = models.BooleanField(default=False) # флаг первичной проводки

    class Meta:
        ordering = ['-id']


class Contact(models.Model):
    contact = models.IntegerField(unique=True) # Код клиента из программы Альта-СВХ
    type = models.CharField(max_length=1, blank=True, default='') # Тип пользователя
    name = models.CharField(max_length=150, blank=True, default='') # Наименование организации
    inn = models.CharField(max_length=12, blank=True, default='') # ИНН организации
    fio = models.CharField(max_length=100, blank=True, default='') # ФИО физлица организации. ФИО оператора СВХ
    email0 = models.CharField(max_length=100, blank=True, default='') # Почта для смены пароля и контактов по работе портала
    email1 = models.CharField(max_length=100, blank=True, default='') # Почта отсылки сообщений
    email2 = models.CharField(max_length=100, blank=True, default='') # Почта для передачи документов партии товара
    idtelegram = models.CharField(max_length=36, blank=True, default='') # Идентификатор ID messenger Telegram
    tags = models.CharField(max_length=100, blank=True, default='') # Список хэштегов
    login = models.CharField(max_length=30, blank=True, default='') # Логин клиента (организации)
    pwd = models.CharField(max_length=20, blank=True, default='') # Пароль входа в портал. Должен быть зашифрован

    f_stop = models.BooleanField(default=False) # Флаг приостановки пользования порталом
    guid_user = models.CharField(max_length=36, blank=True, default='') # GUID пользователя который создал эту запись
    datep = models.DateTimeField(auto_now_add=True) # Дата создания записи

    posted = models.BooleanField(default=False) # флаг проводки
    post_date = models.DateTimeField(blank=True, null=True) # дата проводки
    post_user_id = models.CharField(max_length=36, blank=True, default='') # идентификатор пользователя  который провел запись 


    class Meta:
        ordering = ['-id']
        

class Document(models.Model):
    docnum = models.CharField(max_length=36) # Номер документа
    docdate = models.DateTimeField(blank=True, null=True) # Дата документа
    docname = models.CharField(max_length=100, blank=True, default='') # Наименование документа
    file = models.FileField(upload_to='documents/', blank=True, null=True)

    docbody = models.BinaryField(blank=True, null=True) # Содержимое документа. Может быть zip
    f_zip = models.BooleanField(blank=True, default=False) # файл архивирован/неархивирован
    nfile = models.CharField(max_length=100, blank=True, default='') # Наименование файла
    guid_partia = models.CharField(max_length=100) # Ссылка на партию товара (key_id)
    guid_mail = models.CharField(max_length=36, blank=True, default='') # Uemail.guid. guid письма которое отослал этот документ 
    dates = models.DateTimeField(blank=True, null=True) # Дата отправки письма c документом

    guid_user = models.CharField(max_length=36, blank=True, default='') # GUID пользователя который создал эту запись
    datep = models.DateTimeField(auto_now_add=True) # Дата создания записи


class Message(models.Model):
    guid_partia = models.CharField(max_length=36) # id Партии товара
    contact = models.IntegerField() # Код клиента 
    txt = models.CharField(max_length=200) # Сообщение
    datep = models.DateTimeField(auto_now_add=True) # Дата создания записи
    dater = models.DateTimeField() # Дата прочтения сообщения


class Uemail(models.Model):
    uniqueindexfield = models.BigAutoField(primary_key=True, null=False)
    guid_partia = models.CharField(max_length=36, default='') # Guid партии товара  к которой относиться сообщение
    type = models.CharField(max_length=1, default='') # Тип сообщения: с документами/без документов
    adrto = models.CharField(max_length=200, default='') # Адресат
    subj = models.CharField(max_length=100, default='') # Заголовок сообщения
    textemail = models.CharField(max_length=600, default='') # Текст письма
    attachmentfiles = models.CharField(max_length=200, default='') # Наименование приложенных файлов
    datep = models.DateTimeField(auto_now_add=True) # Дата создания записи
    dates = models.DateTimeField(blank=True, null=True) # Дата отправки письма
    datet = models.DateTimeField(blank=True, null=True) # Дата-время после которого можно отправлять письмо. Сравнивается с текущим временем. Для отсроченной отправки. = NULL -  отправляется немедленно
    datef = models.DateTimeField(blank=True, null=True) # Дата-время после которого отправка птсма бесполезна. = NULL – отправлять всегда
    f_error = models.IntegerField(blank=True, null=True) # Счетчик отправки письма с ошибками - ответ SMTP сервера. Если =3 , то письмо более не отправляется
    errortxt = models.CharField(max_length=100, default='') # Ошибка отправки - ответ SMTP сервера
    id = models.CharField(max_length=8, null=True) # для совместимости в старой таблицей альты

    def __str__(self):
        return self.key_id
    