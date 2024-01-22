from django.urls import path
from . import views
urlpatterns = [
    path("",views.dashbord,name="dashbord"),
    path('order/',views.order,name='order'),
    path('changepassword/',views.changepassword,name="changepassword")
]