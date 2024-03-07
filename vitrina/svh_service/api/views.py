from datetime import datetime
from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from svh_service.models import Consignment, Carpass, Contact, Document, Uemail
from svh_service.api.serializers import StatSerializer, IsAliveSerializer
from django.http import JsonResponse
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]


def get_app_alive(request):
    # api endpoint to get app is_alive status
    current_datetime = datetime.now()
    app_name = 'svh_service'
    is_alive = True

    data = {'current_datetime': current_datetime,
            'app_name': app_name, 
            'is_alive': is_alive,
            }
    
    serializer = IsAliveSerializer(data)
    data_serialized = serializer.data
    
    return JsonResponse(data_serialized, safe=False)


def get_app_stat(request):
    # api endpoint to get app statistics
    current_datetime = datetime.now()
    consignments = Consignment.objects.all()
    carpass = Carpass.objects.all()
    contacts = Contact.objects.all()
    documents = Document.objects.all()
    uemails = Uemail.objects.all()

    data = {'current_datetime': current_datetime,
            'consignments': len(consignments),
            'carpass': len(carpass),
            'contacts': len(contacts),
            'documents': len(documents),
            'uemails': len(uemails),
            }
    
    serializer = StatSerializer(data)
    data_serialized = serializer.data
    
    return JsonResponse(data_serialized, safe=False)
