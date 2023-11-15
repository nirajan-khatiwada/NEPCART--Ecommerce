from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.logins,name="login"),
    path('logout/',views.logouts,name="logout"),
    path('signup/',views.signup,name="signup"),
    path('forgotpassword/',views.forgotpassword,name="forgotpassword"),
    path("activate/<str:username>/",views.activate),
    path("fp_validate/<str:username>/",views.fp_validate),
    path("resetpassword/",views.resetpassword,name="reset")
]
