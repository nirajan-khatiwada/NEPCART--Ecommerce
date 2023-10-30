from django.urls import path
from . import views
urlpatterns = [
    path("",views.store,name="store"),
    path("<slug:category_slug>",views.category_display,name="product_by_category"),
    path("<slug:category_slug>/<slug:product_slug>",views.product_display,name="product_detail")
   
]
