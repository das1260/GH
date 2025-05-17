from django.urls import path
from .views import book_appointment,appointment_success,confirm_payment,test

urlpatterns = [
    path('book/', book_appointment, name='book_appointment'),
    path('success/', appointment_success, name='appointment_success'),
    path('confirm_payment/', confirm_payment, name='confirm_payment'),
    path('test/', test, name='test'),

    # add other URL patterns as needed
]
