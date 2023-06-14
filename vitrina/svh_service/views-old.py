from django.shortcuts import render, get_object_or_404
from .models import Consignment, Contact


def consignment_list(request):
    consignments = Consignment.objects.all()

    return render(request,
                  'shv_service/consignment/list.html',
                  {'consignments': consignments})


def consignment_detail(request, id):
    consignment = get_object_or_404(Consignment, id=id)
    
    return render(request,
                  'shv_service/consignment/detail.html',
                  {'consignment': consignment})

def contact_list(request):
    contacts = Contact.objects.all()

    return render(request,
                  'shv_service/contact/list.html',
                  {'contacts': contacts})


def contact_detail(request, id):
    contact = get_object_or_404(Contact, id=id)
    
    return render(request,
                  'shv_service/contact/detail.html',
                  {'contact': contact})
