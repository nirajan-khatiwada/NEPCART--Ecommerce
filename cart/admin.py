from django.contrib import admin
from .models import Coupon


class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active', 'created_at')
    list_editable = ('discount_percent', 'active')
    search_fields = ('code',)
    list_filter = ('active', 'created_at')


admin.site.register(Coupon, CouponAdmin)
