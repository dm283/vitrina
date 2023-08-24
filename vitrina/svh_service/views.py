import os
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Consignment, Carpass, Contact, Document, Uemail
from .forms import ConsignmentForm, CarpassForm, ContactForm, DocumentForm
from .forms import ConsignmentFiltersForm, CarpassFiltersForm, ContactFiltersForm
from django.views.decorators.http import require_POST
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, Http404
from urllib.parse import quote


#  CONSIGNMENT ******************************************
def consignment_list(request):
    consignments = Consignment.objects.all()
    documents = Document.objects.all()

    # фильтрация данных
    form_filters = ConsignmentFiltersForm()
    if request.method == 'POST':
        form_filters = ConsignmentFiltersForm(data=request.POST)
        if form_filters.is_valid():
            cd = form_filters.cleaned_data
            if cd['key_id']:
                consignments = consignments.filter(key_id=cd['key_id'])
            if cd['contact_name']:
                consignments = consignments.filter(contact_name=cd['contact_name'])
            if cd['broker_name']:
                consignments = consignments.filter(broker_name=cd['broker_name'])
            if cd['nttn']:
                consignments = consignments.filter(nttn=cd['nttn'])
            if cd['dkd']:
                consignments = consignments.filter(dkd=cd['dkd'])
            if cd['dater_from']:
                consignments = consignments.filter(dater__gte=cd['dater_from'])
            if cd['dater_to']:
                consignments = consignments.filter(dater__lte=cd['dater_to'])
            if cd['dateo_from']:
                consignments = consignments.filter(dateo__gte=cd['dateo_from'])
            if cd['dateo_to']:
                consignments = consignments.filter(dateo__lte=cd['dateo_to'])
            if cd['car']:
                consignments = consignments.filter(car=cd['car'])
            if cd['on_terminal']:
                consignments = consignments.filter(dateo__isnull=True)
            else:
                consignments = consignments.filter(dateo__isnull=False)

    return render(request,
                  'shv_service/consignment/list.html',
                  {'consignments': consignments,
                   'documents': documents,
                   'form_filters': form_filters, })


def consignment_add(request):
    # выбираем из бд max key_id, увеличиваем на 1 - это key_id Новой партии
    key_id_list = Consignment.objects.values_list("key_id", flat=True)
    if len(key_id_list) == 0:
        key_id_list = ['0']
    key_id_new = str(max(list(map(int, key_id_list))) + 1)  # key_id_max_from_list_increased_1

    form = ConsignmentForm(initial={'key_id': key_id_new})

    return render(request, 'shv_service/consignment/add.html',
                  {'form': form})

@require_POST
def post_consignment(request):
    form = ConsignmentForm(data=request.POST)
    if form.is_valid:
        form.save()
    
    consignment = Consignment.objects.all().order_by('-id').first()
    form = ConsignmentForm(instance=consignment)
    
    data = {}
    data['block_name'] = 'Партия товаров'
    data['entity'] = 'consignment'
    data['id'] = consignment.key_id

    return render(request,
                  'shv_service/update_universal.html',
                  {'form': form,
                   'data': data,
                   'entity': consignment})


def consignment_update(request, id):
    consignment = get_object_or_404(Consignment, id=id)
 
    try:
        documents = Document.objects.filter(guid_partia=consignment.key_id)
    except:
        documents = ''

    data = {}
    data['block_name'] = 'Партия товаров'
    data['entity'] = 'consignment'
    data['id'] = consignment.key_id

    if request.method == 'POST':
        form = ConsignmentForm(request.POST, instance=consignment)
        if form.is_valid():
            form.save()

            return render(request,
                        'shv_service/update_universal.html',
                        {'form': form,
                         'data': data, 
                         'entity': consignment,
                         'documents': documents})
    else:
        form = ConsignmentForm(instance=consignment)

    return render(request,
                        'shv_service/update_universal.html',
                        {'form': form,
                         'data': data, 
                         'entity': consignment,
                         'documents': documents})


def consignment_delete(request, id):
    consignment = get_object_or_404(Consignment, id=id)
    
    if request.method == 'POST':
        consignment.delete()
        return redirect('/svh_service/consignments')
    
    return render(request,
                  'shv_service/consignment/delete.html',
                  {'consignment': consignment})


def consignment_post(request, id):
    consignment = get_object_or_404(Consignment, id=id)
    
    # СДЕЛАТЬ ФУНКЦИЮ ПРОВЕРКИ ДАННЫХ В ФОРМЕ!!!!

    if request.method == 'POST':
        guid_partia = consignment.key_id
        if consignment.was_posted:
            textemail = f'Добрый день!\n\nВ карточку партии товара {guid_partia} внесены изменения.\n\nСервис Альта-СВХ Витрина.'
        else:
            textemail = f'Добрый день!\n\nСоздана карточка партии товара {guid_partia}.\n\nСервис Альта-СВХ Витрина.'

        consignment.post_user_id = '1'
        consignment.post_date = datetime.now()
        consignment.posted = True
        consignment.was_posted = True  # устанавливается навечно при первичной проводке
        consignment.save()

        # create uemail record about consignment was created or updated
        contact = get_object_or_404(Contact, contact=consignment.contact)
        type = ''
        adrto = contact.email1
        subj = 'Сервис Альта-СВХ Витрина - оповещение'

        #  выбираются документы соответствующей партии с нуловыми датами отправки (dates)
        #  этот механизм нужно лучше потом продумать 
        files_added = Document.objects.filter(guid_partia=consignment.key_id).filter(dates__isnull=True)
        attachmentfiles = ''
        for n, f in enumerate(files_added):
            attachmentfiles += ', ' if len(attachmentfiles) > 0 else ''
            attachmentfiles += str(f.file).partition('/')[2]

        new_uemail = Uemail(
            guid_partia=guid_partia,
            type=type,
            adrto=adrto,
            subj=subj,
            textemail=textemail,
            attachmentfiles=attachmentfiles,
        )
        new_uemail.save()

        # функция пометки документа как отправленного (потом сделать чтобы она добавлялась только после реально отправки сообщения)
        guid_mail = int(Uemail.objects.all().order_by('-uniqueindexfield')[0].uniqueindexfield)  # выбираем id только что созданного письма
        dates = datetime.now()
        for f in files_added:
            f.guid_mail = guid_mail
            f.dates = dates
            f.save()

        return redirect(f'/svh_service/consignments/{consignment.id}/update')
    
    return render(request,
                  'shv_service/consignment/post.html',
                  {'consignment': consignment})


def consignment_rollback(request, id):
    consignment = get_object_or_404(Consignment, id=id)
    
    if request.method == 'POST':
        consignment.post_user_id = ''
        consignment.post_date = None
        consignment.posted = False
        consignment.save()
        return redirect(f'/svh_service/consignments/{consignment.id}/update')
    
    return render(request,
                  'shv_service/consignment/rollback.html',
                  {'consignment': consignment})


def consignment_close(request, id):
    consignment = get_object_or_404(Consignment, id=id)

    if request.method == 'POST':
        return redirect('/svh_service/consignments')
    
    return render(request,
                  'shv_service/consignment/close.html',
                  {'consignment': consignment})


def consignment_add_document(request, id):
    consignment = get_object_or_404(Consignment, id=id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            document = Document.objects.all().order_by('-id').first()
            form = DocumentForm(instance=document)
            return render(request,
                  'shv_service/document/update.html',
                  {
                   'form': form,
                   'document': document,
                   'entity': consignment, 
                #    'consignment_id': consignment.id,
                   })
    else:
        guid_partia = consignment.key_id
        docdate = datetime.now()
        form = DocumentForm(initial={'docdate': docdate, 'guid_partia': guid_partia})
        
    context = {
        'form': form,
        'consignment_id': consignment.id
    }
    
    return render(request, 
                  'shv_service/consignment/add_document.html', 
                  context)


#  DOCUMENT ******************************************
def document_update(request, id):
    document = get_object_or_404(Document, id=id)
    if document.guid_partia:
        entity = get_object_or_404(Consignment, key_id=document.guid_partia)
    elif document.id_enter:
        entity = get_object_or_404(Carpass, id_enter=document.id_enter)

    if request.method == 'POST':
        form = DocumentForm(data=request.POST, files=request.FILES, instance=document)
        
        # form.fields['guid_partia'].widget = form.fields['guid_partia'].hidden_widget()  ###
        
        if form.is_valid():
            form.save()
            document = get_object_or_404(Document, id=id)
            form = DocumentForm(instance=document)
            # form.fields['guid_partia'].widget = form.fields['guid_partia'].hidden_widget()  ###
            # form.fields['id_enter'].widget = form.fields['id_enter'].hidden_widget()  ###

    else:
        form = DocumentForm(instance=document)
        # form.fields['guid_partia'].widget = form.fields['guid_partia'].hidden_widget()  ###
        # form.fields['id_enter'].widget = form.fields['id_enter'].hidden_widget()  ###

    return render(request,
                  'shv_service/document/update.html',
                  {
                   'form': form,
                   'document': document,
                   'entity': entity,
                   })


def document_delete(request, id):
    document = get_object_or_404(Document, id=id)
    data = {}
    if document.guid_partia:
        entity = get_object_or_404(Consignment, key_id=document.guid_partia)
        data['block_name'] = 'Партия товаров'
        data['entity'] = 'consignment'
        data['id'] = entity.key_id
    elif document.id_enter:
        entity = get_object_or_404(Carpass, id_enter=document.id_enter)
        data['block_name'] = 'Пропуск'
        data['entity'] = 'carpass'
        data['id'] = entity.id_enter
    
    if request.method == 'POST':
        document.delete()

        if document.guid_partia:
            form = ConsignmentForm(instance=entity)
            try:
                documents = Document.objects.filter(guid_partia=entity.key_id)
            except:
                documents = ''
        elif document.id_enter:
            form = CarpassForm(instance=entity)
            try:
                documents = Document.objects.filter(id_enter=entity.id_enter)
            except:
                documents = ''

        return render(request,
                    'shv_service/update_universal.html',
                    {'form': form,
                    'data': data, 
                    'entity': entity,
                    'documents': documents,})


    return render(request,
                  'shv_service/document/delete.html',
                  {
                    'document': document,
                  })


def document_close(request, id):
    document = get_object_or_404(Document, id=id)
    if document.guid_partia:
        entity = get_object_or_404(Consignment, key_id=document.guid_partia)
        entity_title = 'consignments'
    elif document.id_enter:
        entity = get_object_or_404(Carpass, id_enter=document.id_enter)
        entity_title = 'carpass'
    # consignment = get_object_or_404(Consignment, key_id=document.guid_partia)

    if request.method == 'POST':
        return redirect(f'/svh_service/{entity_title}/{entity.id}/update')
    
    return render(request,
                  'shv_service/document/close.html',
                  {'document': document})


def document_download(request, id):
    """
    Скачивает документ
    """
    document = get_object_or_404(Document, id=id)
    path = str(document.file)
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            #response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(quote(os.path.basename(file_path)))
            return response
    return Http404


#  CARPASS ******************************************
def carpass_list(request):
    carpasses = Carpass.objects.all()
    documents = Document.objects.all()

    # фильтрация данных
    form_filters = CarpassFiltersForm()
    if request.method == 'POST':
        form_filters = CarpassFiltersForm(data=request.POST)
        if form_filters.is_valid():
            cd = form_filters.cleaned_data
            if cd['id_enter']:
                carpasses = carpasses.filter(id_enter=cd['id_enter'])
            if cd['ncar']:
                carpasses = carpasses.filter(ncar=cd['ncar'])
            if cd['ntir']:
                carpasses = carpasses.filter(ntir=cd['ntir'])
            if cd['nkont']:
                carpasses = carpasses.filter(nkont=cd['nkont'])
            if cd['dateen_from']:
                carpasses = carpasses.filter(dateen__gte=cd['dateen_from'])
            if cd['dateen_to']:
                carpasses = carpasses.filter(dateen__lte=cd['dateen_to'])

    return render(request,
                  'shv_service/carpass/list.html',
                  {'carpasses': carpasses,
                   'documents': documents,
                   'form_filters': form_filters, })


def carpass_add(request):
    # выбираем из бд max key_id, увеличиваем на 1 - это key_id Новой партии
    id_enter_list = Carpass.objects.values_list("id_enter", flat=True)
    if len(id_enter_list) == 0:
        id_enter_list = ['0']
    id_enter_new = str(max(list(map(int, id_enter_list))) + 1)  # key_id_max_from_list_increased_1

    form = CarpassForm(initial={'id_enter': id_enter_new})

    return render(request, 'shv_service/carpass/add.html',
                  {'form': form})

@require_POST
def post_carpass(request):
    form = CarpassForm(data=request.POST)
    if form.is_valid:
        form.save()
    
    carpass = Carpass.objects.all().order_by('-id').first()
    form = CarpassForm(instance=carpass)
    
    data = {}
    data['block_name'] = 'Пропуск'
    data['entity'] = 'carpass'
    data['id'] = carpass.id_enter

    return render(request,
                  'shv_service/update_universal.html',
                  {'form': form,
                   'data': data, 
                   'entity': carpass,})


def carpass_update(request, id):
    carpass = get_object_or_404(Carpass, id=id)
 
    try:
        documents = Document.objects.filter(id_enter=carpass.id_enter)
    except:
        documents = ''

    data = {}
    data['block_name'] = 'Пропуск'
    data['entity'] = 'carpass'
    data['id'] = carpass.id_enter
    
    if request.method == 'POST':
        form = CarpassForm(request.POST, instance=carpass)
        if form.is_valid():
            form.save()
            return render(request,
                        'shv_service/update_universal.html',
                        {'form': form,
                         'data': data, 
                         'entity': carpass,
                         'documents': documents})
    else:
        form = CarpassForm(instance=carpass)

    return render(request,
                  'shv_service/update_universal.html',
                  {
                   'form': form,
                   'data': data, 
                   'entity': carpass,
                   'documents': documents
                   }
                   )


def carpass_post(request, id):
    carpass = get_object_or_404(Carpass, id=id)
    
    # СДЕЛАТЬ ФУНКЦИЮ ПРОВЕРКИ ДАННЫХ В ФОРМЕ!!!!

    if request.method == 'POST':
        id_enter = carpass.id_enter
        if carpass.was_posted:
            textemail = f'Добрый день!\n\nВ карточку пропуска (id: {id_enter}) внесены изменения.\n\nСервис Альта-СВХ Витрина.'
        else:
            textemail = f'Добрый день!\n\nСоздана карточка пропуска (id: {id_enter}).\n\nСервис Альта-СВХ Витрина.'

        carpass.post_user_id = '1'
        carpass.post_date = datetime.now()
        carpass.posted = True
        carpass.was_posted = True  # устанавливается навечно при первичной проводке
        carpass.save()

        # create uemail record about consignment was created or updated
        contact = get_object_or_404(Contact, contact=carpass.contact)
        type = ''
        adrto = contact.email1
        subj = 'Сервис Альта-СВХ Витрина - оповещение'

        #  выбираются документы соответствующей партии с нуловыми датами отправки (dates)
        #  этот механизм нужно лучше потом продумать 
        files_added = Document.objects.filter(id_enter=carpass.id_enter).filter(dates__isnull=True)
        attachmentfiles = ''
        for n, f in enumerate(files_added):
            attachmentfiles += ', ' if len(attachmentfiles) > 0 else ''
            attachmentfiles += str(f.file).partition('/')[2]

        new_uemail = Uemail(
            id_enter=id_enter,
            type=type,
            adrto=adrto,
            subj=subj,
            textemail=textemail,
            attachmentfiles=attachmentfiles,
        )
        new_uemail.save()

        # функция пометки документа как отправленного (потом сделать чтобы она добавлялась только после реально отправки сообщения)
        guid_mail = int(Uemail.objects.all().order_by('-uniqueindexfield')[0].uniqueindexfield)  # выбираем id только что созданного письма
        dates = datetime.now()
        for f in files_added:
            f.guid_mail = guid_mail
            f.dates = dates
            f.save()

        return redirect(f'/svh_service/carpass/{carpass.id}/update')
    
    return render(request,
                  'shv_service/carpass/post.html',
                  {'carpass': carpass})


def carpass_rollback(request, id):
    carpass = get_object_or_404(Carpass, id=id)
    
    if request.method == 'POST':
        carpass.post_user_id = ''
        carpass.post_date = None
        carpass.posted = False
        carpass.save()
        return redirect(f'/svh_service/carpass/{carpass.id}/update')
    
    return render(request,
                  'shv_service/carpass/rollback.html',
                  {'carpass': carpass})


def carpass_delete(request, id):
    carpass = get_object_or_404(Carpass, id=id)
    
    if request.method == 'POST':
        carpass.delete()
        return redirect('/svh_service/carpass')
    
    return render(request,
                  'shv_service/carpass/delete.html',
                  {'carpass': carpass})


def carpass_close(request, id):
    carpass = get_object_or_404(Carpass, id=id)

    if request.method == 'POST':
        return redirect('/svh_service/carpass')
    
    return render(request,
                  'shv_service/carpass/close.html',
                  {'carpass': carpass})


def carpass_add_document(request, id):
    carpass = get_object_or_404(Carpass, id=id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            document = Document.objects.all().order_by('-id').first()
            form = DocumentForm(instance=document)
            return render(request,
                  'shv_service/document/update.html',
                  {
                   'form': form,
                   'document': document,
                   'entiry': carpass,
                   })
    else:
        id_enter = carpass.id_enter
        docdate = datetime.now()
        form = DocumentForm(initial={'docdate': docdate, 'id_enter': id_enter})
        
    context = {
        'form': form,
        'carpass_id': carpass.id
    }
    
    return render(request, 
                  'shv_service/carpass/add_document.html', 
                  context)


#  CONTACT ******************************************
def contact_list(request):
    contacts = Contact.objects.all()

    # фильтрация данных
    form_filters = ContactFiltersForm()
    if request.method == 'POST':
        form_filters = ContactFiltersForm(data=request.POST)
        if form_filters.is_valid():
            cd = form_filters.cleaned_data
            if cd['contact']:
                contacts = contacts.filter(contact=cd['contact'])
            if cd['type']:
                contacts = contacts.filter(type=cd['type'])
            if cd['name']:
                contacts = contacts.filter(name=cd['name'])
            if cd['inn']:
                contacts = contacts.filter(inn=cd['inn'])
            if cd['email1']:
                contacts = contacts.filter(email1=cd['email1'])
            if cd['idtelegram']:
                contacts = contacts.filter(idtelegram=cd['idtelegram'])


    return render(request,
                  'shv_service/contact/list.html',
                  {'contacts': contacts,
                   'form_filters': form_filters, })


def contact_add(request):
    # # выбираем из бд max contact, увеличиваем на 1 - это contact Новой организации
    contact_list = Contact.objects.values_list("contact", flat=True)
    if len(contact_list) == 0:
        contact_list = ['0']
    contact_new = str(max(list(map(int, contact_list))) + 1)  # key_id_max_from_list_increased_1
    form = ContactForm(initial={'contact': contact_new})

    return render(request, 'shv_service/contact/add.html',
                  {'form': form})

@require_POST
def post_contact(request):
    form = ContactForm(data=request.POST)
    if form.is_valid:
        form.save()

    contact = Contact.objects.all().order_by('-id').first()
    form = ContactForm(instance=contact)

    data = {}
    data['block_name'] = 'Организация'
    data['entity'] = 'contact'
    data['id'] = contact.contact

    return render(request,
                  'shv_service/update_universal.html',
                  {'form': form,
                   'data': data, 
                   'entity': contact,})


def contact_update(request, id):
    contact = get_object_or_404(Contact, id=id)

    data = {}
    data['block_name'] = 'Организация'
    data['entity'] = 'contact'
    data['id'] = contact.contact

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return render(request,
                        'shv_service/update_universal.html',
                        {'form': form,
                         'data': data, 
                         'entity': contact,})
    else:
        form = ContactForm(instance=contact)

    return render(request,
                  'shv_service/update_universal.html',
                  {'form': form,
                   'data': data, 
                   'entity': contact,})


def contact_delete(request, id):
    contact = get_object_or_404(Contact, id=id)
    
    if request.method == 'POST':
        contact.delete()
        return redirect('/svh_service/contacts')
    
    return render(request,
                  'shv_service/contact/delete.html',
                  {'contact': contact})


def contact_post(request, id):
    contact = get_object_or_404(Contact, id=id)
    
    if request.method == 'POST':
        contact.post_user_id = '1'
        contact.post_date = datetime.now()
        contact.posted = True
        contact.save()
        return redirect(f'/svh_service/contacts/{contact.id}/update')
    
    return render(request,
                  'shv_service/contact/post.html',
                  {'contact': contact})


def contact_rollback(request, id):
    contact = get_object_or_404(Contact, id=id)
    
    if request.method == 'POST':
        contact.post_user_id = ''
        contact.post_date = None
        contact.posted = False
        contact.save()
        return redirect(f'/svh_service/contacts/{contact.id}/update')
    
    return render(request,
                  'shv_service/contact/rollback.html',
                  {'contact': contact})


def contact_close(request, id):
    contact = get_object_or_404(Contact, id=id)

    if request.method == 'POST':
        return redirect('/svh_service/contacts')
    
    return render(request,
                  'shv_service/contact/close.html',
                  {'contact': contact})
