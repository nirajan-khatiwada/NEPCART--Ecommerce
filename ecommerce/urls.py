from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from . import views

# Custom Admin Site Branding
admin.site.site_header = "NepCart Admin"
admin.site.site_title = "NepCart Management Portal"
admin.site.index_title = "Welcome to NepCart Management Portal"

# Admin Live Sales Analytics Dashboard Context Injector
original_admin_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    if extra_context is None:
        extra_context = {}

    try:
        from order.models import Order
        from product.models import Product
        from account.models import Account

        orders = Order.objects.filter(status='Paid')
        total_revenue = sum(o.order_total for o in orders)
        total_orders_count = Order.objects.count()
        total_products_count = Product.objects.count()
        total_users_count = Account.objects.count()

        extra_context.update({
            'total_revenue': round(total_revenue, 2),
            'total_orders_count': total_orders_count,
            'total_products_count': total_products_count,
            'total_users_count': total_users_count,
        })
    except Exception:
        pass

    return original_admin_index(request, extra_context=extra_context)

admin.site.index = custom_admin_index


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name="homepage"),
    path("store/", include("store.urls")),
    path("cart/", include("cart.urls")),
    path("auth/", include("account.urls")),
    path('account/', include("dashbord.urls")),
    path('order/', include("order.urls")),
    path('search/', include("search.urls")),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]