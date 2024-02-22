import sys, os, json, configparser
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Consignment, Carpass, Contact, Document, Uemail
from .forms import ConsignmentForm, CarpassForm, ContactForm, DocumentForm
from .forms import ConsignmentFiltersForm, CarpassFiltersForm, ContactFiltersForm
from django.views.decorators.http import require_POST
from datetime import datetime, date
from django.conf import settings
from django.http import HttpResponse, Http404
from urllib.parse import quote
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

from django.contrib.auth import authenticate, login
from .forms import LoginForm
from pathlib import Path
from django.core.exceptions import ValidationError


config = configparser.ConfigParser()
config_file = os.path.join(Path(__file__).resolve().parent.parent, 'vitrina', 'config.ini')
if os.path.exists(config_file):
    config.read(config_file, encoding='utf-8')
else:
    print("error! config file doesn't exist"); sys.exit()

APP_TYPE = config['app']['app_type']
FILE_FILTERS = {}

TYPE_NAME = {
            "V": "участник ВЭД", 
            "B": "таможенный представитель (брокер)", 
            "O": "оператор СВХ", 
            "H": "руководство СВХ",
        }

# COMMON_VIEWS - CONSIGNMENT - CARPASS - DOCUMENT - CONTACT

#  COMMON_VIEWS *************************************
@login_required
def erase_filters(request, entity):
    # erase all filters data - by deleting json file with it
    if os.path.exists(FILE_FILTERS[entity]):
        os.remove(FILE_FILTERS[entity])
    return redirect(f'/svh_service/{entity}')


@login_required
def object_add(request, entity_type):
    # universal function for adding object (consignment, carpass, contact)

    entity, entity['consignment'], entity['carpass'] = {}, {}, {}
    entity['consignment'] = { 'model': Consignment, 'id_name': 'key_id' }
    entity['carpass'] = { 'model': Carpass, 'id_name': 'id_enter' }
    entity['contact'] = { 'model': Contact, 'id_name': 'contact' }

    # calculate new object id = get from db max related to entity_type (model) ID and increase it on 1
    object_id_list = entity[entity_type]['model'].objects.values_list(
        entity[entity_type]['id_name'], flat=True)
    if len(object_id_list) == 0:
        object_id_list = ['0']
    object_id_new = max(list(map(int, object_id_list))) + 1
    object_id_new = int(object_id_new) if entity_type == 'contact' else str(object_id_new)

    # create empty object with entity id only and save it to db
    c = entity[entity_type]['model']()
    c.__setattr__(entity[entity_type]['id_name'], object_id_new)
    c.save()

    # get id or the newest created object and redirect to update page
    get_object = entity[entity_type]['model'].objects.all().order_by('-id')[0]
    id_for_link = get_object.id
    entity_type_for_link = entity_type if entity_type == 'carpass' else entity_type+'s'
    return redirect(f'/svh_service/{entity_type_for_link}/{id_for_link}/update')


#  CONSIGNMENT ******************************************
@login_required
def consignment_list(request):
    """
    Список партии товаров
    """
    global FILE_FILTERS
    CONTACT_FOLDER = f'temp_files/{request.user.profile.contact}'
    FILE_FILTERS['consignments'] = CONTACT_FOLDER + '/consignments_filters.json'
    FILE_FILTERS['carpass'] = CONTACT_FOLDER + '/carpass_filters.json'
    FILE_FILTERS['contacts'] = CONTACT_FOLDER + '/contacts_filters.json'
    if not os.path.exists('temp_files'):
        os.mkdir('temp_files')
    if not os.path.exists(CONTACT_FOLDER):
        os.mkdir(CONTACT_FOLDER)

    if request.user.profile.type == 'O' and APP_TYPE == 'operator':
        consignments = Consignment.objects.all()
        documents = Document.objects.all()
    elif request.user.profile.type == 'O' and APP_TYPE == 'client':
        # if client try to login as operator svh
        return redirect('/svh_service/login')
    else:
        try:
            if request.user.profile.type == 'V':
                consignments = Consignment.objects.filter(posted=True).filter(contact=request.user.profile.contact)
            elif request.user.profile.type == 'B':
                consignments = Consignment.objects.filter(posted=True).filter(contact_broker=request.user.profile.contact)
        except:
            consignments = ''

        try:
            key_id_list = consignments.values_list("key_id", flat=True)
            documents = Document.objects.filter(guid_partia__in=key_id_list)
        except:
            documents = ''

    # фильтрация данных
    if request.method == 'POST':
        form_filters = ConsignmentFiltersForm(data=request.POST)
        if form_filters.is_valid():
            cd = form_filters.cleaned_data
            # save filters data into json file
            # cast datetime to str for ability of serializing
            cd_date_casted = form_filters.cleaned_data
            for d in cd_date_casted:
                if (type(cd_date_casted[d]) is date):
                    cd_date_casted[d] = cd_date_casted[d].strftime('%Y-%m-%d')
            cd_json = json.dumps(cd_date_casted)
            with open(FILE_FILTERS['consignments'], 'w', encoding='utf-8') as f:
                f.write(cd_json)

    else: # request.method == 'GET'
        # load filters data from json file if it exists
        if os.path.exists(FILE_FILTERS['consignments']):
            with open(FILE_FILTERS['consignments'], 'r') as f:
                cd = json.load(f)
            form_filters = ConsignmentFiltersForm(initial=cd)
        # create empty form if json file doesn't exit
        else:
            form_filters = ConsignmentFiltersForm()
            return render(request,
                    'shv_service/consignment/list.html',
                    {'consignments': consignments,
                    'documents': documents,
                    'form_filters': form_filters, })
    
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
    # else:
    #     consignments = consignments.filter(dateo__isnull=False)

    return render(request,
                  'shv_service/consignment/list.html',
                  {'consignments': consignments,
                   'documents': documents,
                   'form_filters': form_filters, })


# @login_required
# def consignment_add(request):
#     # выбираем из бд max key_id, увеличиваем на 1 - это key_id Новой партии
#     key_id_list = Consignment.objects.values_list("key_id", flat=True)
#     if len(key_id_list) == 0:
#         key_id_list = ['0']
#     key_id_new = str(max(list(map(int, key_id_list))) + 1)  # key_id_max_from_list_increased_1

#     c = Consignment(key_id=key_id_new)
#     c.save()
#     consignment = get_object_or_404(Consignment, key_id=key_id_new)

#     return redirect(f'/svh_service/consignments/{consignment.id}/update')


    # form = ConsignmentForm(initial={'key_id': key_id_new})

    # return render(request, 'shv_service/consignment/add.html',
    #               {'form': form})



# @login_required
# def consignment_add(request):
#     # выбираем из бд max key_id, увеличиваем на 1 - это key_id Новой партии
#     key_id_list = Consignment.objects.values_list("key_id", flat=True)
#     if len(key_id_list) == 0:
#         key_id_list = ['0']
#     key_id_new = str(max(list(map(int, key_id_list))) + 1)  # key_id_max_from_list_increased_1

#     form = ConsignmentForm(initial={'key_id': key_id_new})

#     return render(request, 'shv_service/consignment/add.html',
#                   {'form': form})

# @login_required
# @require_POST
# def post_consignment(request):
#     form = ConsignmentForm(data=request.POST)
#     if form.is_valid:
#         form.save()
    
#     consignment = Consignment.objects.all().order_by('-id').first()

#     return redirect(f'/svh_service/consignments/{consignment.id}/update')    #####

    # form = ConsignmentForm(instance=consignment)
    
    # data = {}
    # data['block_name'] = 'Партия товаров'
    # data['entity'] = 'consignment'
    # data['id'] = consignment.key_id

    # return render(request,
    #               'shv_service/update_universal.html',
    #               {'form': form,
    #                'data': data,
    #                'entity': consignment})


@login_required
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


@login_required
def consignment_delete(request, id):
    consignment = get_object_or_404(Consignment, id=id)
    
    if request.method == 'POST':
        consignment.delete()
        return redirect('/svh_service/consignments')
    
    return render(request,
                  'shv_service/consignment/delete.html',
                  {'consignment': consignment})


@login_required
def consignment_post(request, id):
    consignment = get_object_or_404(Consignment, id=id)

    # ПРОВЕРКИ ДАННЫХ
    try:
        get_object_or_404(Contact, contact=consignment.contact)
        is_approved = True
        error_msg = []
    except:
        is_approved = False
        error_msg = ['Данные указанного клиента не заведены в разделе Организации']

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

    link_for_cancel = mark_safe(f'<a href="/svh_service/consignments/{id}/update">')

    return render(request,
                'shv_service/post_universal.html',
                  {'is_approved': is_approved,
                   'error_msg': error_msg,
                   'link_for_cancel': link_for_cancel})


@login_required
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


@login_required
def consignment_close(request, id):
    consignment = get_object_or_404(Consignment, id=id)

    if request.method == 'POST':
        return redirect('/svh_service/consignments')
    
    return render(request,
                  'shv_service/consignment/close.html',
                  {'consignment': consignment})




# @login_required
# def consignment_add_document(request, id):
#     consignment = get_object_or_404(Consignment, id=id)

#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():

#             if request.FILES:
#                 # actions for save file as binary to database
#                 form = save_file_as_blob_to_database(form, request.FILES['file'])

#             form.save()
#             document = Document.objects.all().order_by('-id').first()
#             return redirect(f'/svh_service/documents/{document.id}/update')

#     else:
#         guid_partia = consignment.key_id
#         docdate = datetime.now()
#         form = DocumentForm(initial={'docdate': docdate, 'guid_partia': guid_partia})
        
#     context = {
#         'form': form,
#         'consignment_id': consignment.id
#     }
    
#     return render(request, 
#                   'shv_service/consignment/add_document.html', 
#                   context)



#  CARPASS ******************************************
@login_required
def carpass_list(request):
    if request.user.profile.type == 'O' and APP_TYPE == 'operator':
        carpasses = Carpass.objects.all()
        documents = Document.objects.all()
    else:
        try:
            if request.user.profile.type == 'V':
                carpasses = Carpass.objects.filter(posted=True).filter(contact=request.user.profile.contact)
            elif request.user.profile.type == 'B':
                carpasses = Carpass.objects.filter(posted=True).filter(contact_broker=request.user.profile.contact)
        except:
            carpasses = ''

        try:
            id_enter_list = carpasses.values_list("id_enter", flat=True)
            documents = Document.objects.filter(id_enter__in=id_enter_list)
        except:
            documents = ''

    # фильтрация данных
    if request.method == 'POST':
        form_filters = CarpassFiltersForm(data=request.POST)
        if form_filters.is_valid():
            cd = form_filters.cleaned_data
            # save filters data into json file
            # cast datetime to str for ability of serializing
            cd_date_casted = form_filters.cleaned_data
            for d in cd_date_casted:
                if (type(cd_date_casted[d]) is date):
                    cd_date_casted[d] = cd_date_casted[d].strftime('%Y-%m-%d')
            cd_json = json.dumps(cd_date_casted)
            if not os.path.exists('temp_files'):
                os.mkdir('temp_files')
            with open(FILE_FILTERS['carpass'], 'w', encoding='utf-8') as f:
                f.write(cd_json)

    else: # request.method == 'GET'
        # load filters data from json file if it exists
        if os.path.exists(FILE_FILTERS['carpass']):
            with open(FILE_FILTERS['carpass'], 'r') as f:
                cd = json.load(f)
            form_filters = CarpassFiltersForm(initial=cd)
        # create empty form if json file doesn't exit
        else:
            form_filters = CarpassFiltersForm()
            return render(request,
                    'shv_service/carpass/list.html',
                    {'carpasses': carpasses,
                    'documents': documents,
                    'form_filters': form_filters, })
        
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



# @login_required
# def carpass_add(request):
#     # выбираем из бд max key_id, увеличиваем на 1 - это key_id Новой партии
#     id_enter_list = Carpass.objects.values_list("id_enter", flat=True)
#     if len(id_enter_list) == 0:
#         id_enter_list = ['0']
#     id_enter_new = str(max(list(map(int, id_enter_list))) + 1)  # key_id_max_from_list_increased_1

#     c = Carpass(id_enter=id_enter_new)
#     c.save()
#     carpass = get_object_or_404(Carpass, id_enter=id_enter_new)

#     return redirect(f'/svh_service/carpass/{carpass.id}/update')


# @login_required
# def carpass_add(request):
#     # выбираем из бд max key_id, увеличиваем на 1 - это key_id Новой партии
#     id_enter_list = Carpass.objects.values_list("id_enter", flat=True)
#     if len(id_enter_list) == 0:
#         id_enter_list = ['0']
#     id_enter_new = str(max(list(map(int, id_enter_list))) + 1)  # key_id_max_from_list_increased_1

#     form = CarpassForm(initial={'id_enter': id_enter_new})

#     return render(request, 'shv_service/carpass/add.html',
#                   {'form': form})

# @login_required
# @require_POST
# def post_carpass(request):
#     form = CarpassForm(data=request.POST)
#     if form.is_valid:
#         form.save()
    
#     carpass = Carpass.objects.all().order_by('-id').first()

#     return redirect(f'/svh_service/carpass/{carpass.id}/update')    #####

    # form = CarpassForm(instance=carpass)
    
    # data = {}
    # data['block_name'] = 'Пропуск'
    # data['entity'] = 'carpass'
    # data['id'] = carpass.id_enter

    # return render(request,
    #               'shv_service/update_universal.html',
    #               {'form': form,
    #                'data': data, 
    #                'entity': carpass,})


@login_required
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


@login_required
def carpass_post(request, id):
    carpass = get_object_or_404(Carpass, id=id)
    
    # ПРОВЕРКИ ДАННЫХ
    try:
        get_object_or_404(Contact, contact=carpass.contact)
        is_approved = True
        error_msg = []
    except:
        is_approved = False
        error_msg = ['Данные указанного клиента не заведены в разделе Организации']

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
    
    link_for_cancel = mark_safe(f'<a href="/svh_service/carpass/{id}/update">')

    return render(request,
                'shv_service/post_universal.html',
                  {'is_approved': is_approved,
                   'error_msg': error_msg,
                   'link_for_cancel': link_for_cancel})

    # return render(request,
    #               'shv_service/carpass/post.html',
    #               {'carpass': carpass,
    #                'is_approved': is_approved,
    #                'error_msg': error_msg,
    #                })


@login_required
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


@login_required
def carpass_delete(request, id):
    carpass = get_object_or_404(Carpass, id=id)
    
    if request.method == 'POST':
        carpass.delete()
        return redirect('/svh_service/carpass')
    
    return render(request,
                  'shv_service/carpass/delete.html',
                  {'carpass': carpass})


@login_required
def carpass_close(request, id):
    carpass = get_object_or_404(Carpass, id=id)

    if request.method == 'POST':
        return redirect('/svh_service/carpass')
    
    return render(request,
                  'shv_service/carpass/close.html',
                  {'carpass': carpass})


# @login_required
# def carpass_add_document(request, id):
#     carpass = get_object_or_404(Carpass, id=id)

#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():

#             if request.FILES:
#                 # actions for save file as binary to database
#                 form = save_file_as_blob_to_database(form, request.FILES['file'])

#             form.save()
#             document = Document.objects.all().order_by('-id').first()
#             return redirect(f'/svh_service/documents/{document.id}/update')

#     else:
#         id_enter = carpass.id_enter
#         docdate = datetime.now()
#         form = DocumentForm(initial={'docdate': docdate, 'id_enter': id_enter})
        
#     context = {
#         'form': form,
#         'carpass_id': carpass.id
#     }
    
#     return render(request, 
#                   'shv_service/carpass/add_document.html', 
#                   context)



#  DOCUMENT ******************************************
def save_file_as_blob_to_database(form, file):
    # actions for save file as binary to database
    nfile = file.name
    docbody = file.read()
    new_form = form.save(commit=False)
    new_form.nfile = nfile
    new_form.docbody = docbody
    # new_form.file = ''  #  if uncommented - don't saves uploaded files into filesystem, only into database
    form = new_form

    return form


@login_required
def document_add(request, entity_type, entity_id):  # new 22.02.2024 function!
    # entity_type in ['consignment', 'carpass]  # id = entity.id
    entity, entity['consignment'], entity['carpass'] = {}, {}, {}
    entity['consignment']['model'] = Consignment
    entity['carpass']['model'] = Carpass
    get_object = get_object_or_404(entity[entity_type]['model'], id=entity_id)
    if entity_type == 'consignment':
        entity_specific_id = get_object.key_id
    elif entity_type == 'carpass':
        entity_specific_id = get_object.id_enter

    entity['consignment']['entity_id_type'] = 'guid_partia'
    entity['carpass']['entity_id_type'] = 'id_enter'

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES:
                # actions for save file as binary to database
                form = save_file_as_blob_to_database(form, request.FILES['file'])
            form.save()
            document = Document.objects.all().order_by('-id').first()
            return redirect(f'/svh_service/documents/{document.id}/update')

    else:
        docdate = datetime.now()
        form = DocumentForm(initial={'docdate': docdate,  entity[entity_type]['entity_id_type']: entity_specific_id})
        
    id_for_link = get_object.id
    entity_type_for_link = entity_type + 's' if entity_type == 'consignment' else entity_type
    link_for_cancel = mark_safe(f'<a href="/svh_service/{entity_type_for_link}/{id_for_link}/update">')

    context = {
        'form': form,
        'entity_type': entity_type,
        'entity_id': get_object.id,
        'link_for_cancel': link_for_cancel
    }
    
    return render(request, 
                  'shv_service/document_add.html', 
                  context)


@login_required
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
            if request.FILES:
                # actions for save file as binary to database
                form = save_file_as_blob_to_database(form, request.FILES['file'])

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


@login_required
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


@login_required
def document_close(request, id):
    document = get_object_or_404(Document, id=id)
    if document.guid_partia:
        entity = get_object_or_404(Consignment, key_id=document.guid_partia)
        entity_title = 'consignments'
    elif document.id_enter:
        entity = get_object_or_404(Carpass, id_enter=document.id_enter)
        entity_title = 'carpass'

    if request.method == 'POST':
        return redirect(f'/svh_service/{entity_title}/{entity.id}/update')
    
    return render(request,
                  'shv_service/document/close.html',
                  {'document': document})


@login_required
def document_download(request, id):
    """
    Downloads a file from blob in database to downloads folder in filesystem
    """
    document = get_object_or_404(Document, id=id)
    filename = document.nfile
    blob = document.docbody
    response = HttpResponse(blob, content_type="text/plain")
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(quote(os.path.basename(filename)))
    return response

    # var 1 - from filesystem
    # document = get_object_or_404(Document, id=id)
    # path = str(document.file)
    # file_path = os.path.join(settings.MEDIA_ROOT, path)
    # if os.path.exists(file_path):
    #     with open(file_path, 'rb') as fh:
    #         response = HttpResponse(fh.read(), content_type="text/plain")
    #         #response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
    #         response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(quote(os.path.basename(file_path)))
    #         return response
    # return Http404

    # var 2 - from blob in db
    # document = get_object_or_404(Document, id=id)
    # filename = document.nfile
    # blob = document.docbody
    # with open(os.path.join(FOLDER_DOWNLOADED_FILES, filename), 'wb') as file:
    #     file.write(blob)



#  CONTACT ******************************************
@login_required
def contact_list(request):
    contacts = Contact.objects.all()

    # фильтрация данных
    if request.method == 'POST':
        form_filters = ContactFiltersForm(data=request.POST)
        if form_filters.is_valid():
            cd = form_filters.cleaned_data
            # save filters data into json file
            # cast datetime to str for ability of serializing
            cd_date_casted = form_filters.cleaned_data
            for d in cd_date_casted:
                if (type(cd_date_casted[d]) is date):
                    cd_date_casted[d] = cd_date_casted[d].strftime('%Y-%m-%d')
            cd_json = json.dumps(cd_date_casted)
            if not os.path.exists('temp_files'):
                os.mkdir('temp_files')
            with open(FILE_FILTERS['contacts'], 'w', encoding='utf-8') as f:
                f.write(cd_json)

    else: # request.method == 'GET'
        # load filters data from json file if it exists
        if os.path.exists(FILE_FILTERS['contacts']):
            with open(FILE_FILTERS['contacts'], 'r') as f:
                cd = json.load(f)
            form_filters = ContactFiltersForm(initial=cd)
        # create empty form if json file doesn't exit
        else:
            form_filters = ContactFiltersForm()
            return render(request,
                    'shv_service/contact/list.html',
                    {'contacts': contacts,
                    'form_filters': form_filters, })

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



# @login_required
# def contact_add(request):
#     # creates a new record in database with generated 'contact' field and then redirects to update page
#     contact_list = Contact.objects.values_list("contact", flat=True)
#     if len(contact_list) == 0:
#         contact_list = ['0']
#     contact_new = int(max(list(map(int, contact_list))) + 1)  # max existing contact number from db increased on 1
#     c = Contact(contact=contact_new)
#     c.save()
#     contact = get_object_or_404(Contact, contact=contact_new)

#     return redirect(f'/svh_service/contacts/{contact.id}/update')
    

@login_required
def contact_update(request, id):
    # update page
    contact = get_object_or_404(Contact, id=id)

    data = {}
    data['block_name'] = 'Организация'
    data['entity'] = 'contact'
    data['id'] = contact.contact

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            new_form = form.save(commit=False)
            # create type name depends on type litera
            form_type = form.cleaned_data['type']
            new_form.type_name = TYPE_NAME[form_type]
            new_form.save()

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


@login_required
def contact_delete(request, id):
    contact = get_object_or_404(Contact, id=id)
    
    if request.method == 'POST':
        contact.delete()
        return redirect('/svh_service/contacts')
    
    return render(request,
                  'shv_service/contact/delete.html',
                  {'contact': contact})


@login_required
def contact_post(request, id):
    contact = get_object_or_404(Contact, id=id)

    # ПРОВЕРКИ ДАННЫХ
    check_fields = {'name': 'Наименование организации', 
            'inn': 'ИНН организации', 
            'fio': 'ФИО представителя', 
            'email0': 'Почта для смены пароля и контактов по работе портала', 
            'email1': 'Почта отсылки сообщений', 
            'email2': 'Почта для передачи документов партии товара', }
    #check_fields = list(check_fields.keys())
    #['name', 'inn', 'fio', 'email0', 'email1', 'email2']
    entity_fields = contact.__dict__
    empty_fields_list = []
    for e in list(check_fields.keys()):
        if entity_fields[e] in ['', None]:
            empty_fields_list.append(f'[ {check_fields[e]} ] не заполнено')
    if len(empty_fields_list) > 0:
        is_approved = False
        error_msg = empty_fields_list
        print(error_msg)
    else:
        is_approved = True
        error_msg = []
    
    if request.method == 'POST':
        contact.post_user_id = '1'
        contact.post_date = datetime.now()
        contact.posted = True
        contact.save()
        return redirect(f'/svh_service/contacts/{contact.id}/update')
    
    link_for_cancel = mark_safe(f'<a href="/svh_service/contacts/{id}/update">')

    return render(request,
                'shv_service/post_universal.html',
                  {'is_approved': is_approved,
                   'error_msg': error_msg,
                   'link_for_cancel': link_for_cancel})


@login_required
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


@login_required
def contact_close(request, id):
    contact = get_object_or_404(Contact, id=id)

    if request.method == 'POST':
        return redirect('/svh_service/contacts')
    
    return render(request,
                  'shv_service/contact/close.html',
                  {'contact': contact})
