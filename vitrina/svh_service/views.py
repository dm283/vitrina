from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Consignment, Contact, Document, Uemail
from .forms import ConsignmentForm, ContactForm, DocumentForm
from django.views.decorators.http import require_POST
from datetime import datetime


#  CONSIGNMENT ******************************************
def consignment_list(request):
    consignments = Consignment.objects.all()

    return render(request,
                  'shv_service/consignment/list.html',
                  {'consignments': consignments})


def consignment_add(request):
    # выбираем из бд max key_id, увеличиваем на 1 - это key_id Новой партии
    key_id_list = Consignment.objects.values_list("key_id", flat=True)
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
    
    return render(request,
                  'shv_service/consignment/update.html',
                  {'form': form,
                   'consignment': consignment})


def consignment_update(request, id):
    consignment = get_object_or_404(Consignment, id=id)
 
    try:
        documents = Document.objects.filter(guid_partia=consignment.key_id)
    except:
        documents = ''

    if request.method == 'POST':
        form = ConsignmentForm(request.POST, instance=consignment)
        if form.is_valid():
            form.save()
            return render(request,
                        'shv_service/consignment/update.html',
                        {'form': form,
                         'consignment': consignment})
    else:
        form = ConsignmentForm(instance=consignment)

    return render(request,
                  'shv_service/consignment/update.html',
                  {
                   'form': form,
                   'consignment': consignment,
                   'documents': documents
                   }
                   )


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
            attachmentfiles += ', ' if n > 0 else ''
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
        #return HttpResponse('Откат проводки партии товаров успешно осуществлен.')
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


def document_update(request, id):
    document = get_object_or_404(Document, id=id)
    consignment = get_object_or_404(Consignment, key_id=document.guid_partia)

    if request.method == 'POST':
        form = DocumentForm(data=request.POST, files=request.FILES, instance=document)
        if form.is_valid():
            form.save()
            document = get_object_or_404(Document, id=id)
            form = DocumentForm(instance=document)

    else:
        form = DocumentForm(instance=document)

    return render(request,
                  'shv_service/document/update.html',
                  {
                   'form': form,
                   'document_id': document.id,
                   'consignment': consignment,
                   })


def document_delete(request, id):
    document = get_object_or_404(Document, id=id)
    consignment = get_object_or_404(Consignment, key_id=document.guid_partia)
    
    if request.method == 'POST':
        document.delete()
        form = ConsignmentForm(instance=consignment)
        try:
            documents = Document.objects.filter(guid_partia=consignment.key_id)
        except:
            documents = ''

        return render(request,
                  'shv_service/consignment/update.html',
                  {
                   'form': form,
                   'consignment': consignment,
                   'documents': documents
                   }
                   )
    
    return render(request,
                  'shv_service/document/delete.html',
                  {
                    'document': document,
                    # 'consignment_id': consignment.id,
                  })


def document_close(request, id):
    document = get_object_or_404(Document, id=id)
    consignment = get_object_or_404(Consignment, key_id=document.guid_partia)

    
    if request.method == 'POST':
        return redirect(f'/svh_service/consignments/{consignment.id}/update')
    
    return render(request,
                  'shv_service/document/close.html',
                  {'document': document})


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
                   'document_id': document.id,
                   'consignment_id': consignment.id,
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




#  CONTACT ******************************************
def contact_list(request):
    contacts = Contact.objects.all()

    return render(request,
                  'shv_service/contact/list.html',
                  {'contacts': contacts})


def contact_add(request):
    # # выбираем из бд max contact, увеличиваем на 1 - это contact Новой организации
    # contact_list = Contact.objects.values_list("contact", flat=True)
    # contact_new = max(list(contact_list)) + 1
    # form = ContactForm(initial={'contact': contact_new})
    form = ContactForm()

    return render(request, 'shv_service/contact/add.html',
                  {'form': form})

@require_POST
def post_contact(request):
    form = ContactForm(data=request.POST)
    if form.is_valid:
        form.save()

    contact = Contact.objects.all().order_by('-id').first()
    form = ContactForm(instance=contact)
    
    return render(request,
                  'shv_service/contact/update.html',
                  {'form': form,
                   'contact': contact})


def contact_update(request, id):
    contact = get_object_or_404(Contact, id=id)

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return render(request,
                        'shv_service/contact/update.html',
                        {'form': form,
                         'contact': contact})
    else:
        form = ContactForm(instance=contact)

    return render(request,
                  'shv_service/contact/update.html',
                  {'form': form,
                   'contact': contact})


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
