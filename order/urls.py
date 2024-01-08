from django.urls import path
from . import views

urlpatterns = [
    path("payment/",views.payment,name='payment'),
    path('verify/',views.verify,name="verify")
]
