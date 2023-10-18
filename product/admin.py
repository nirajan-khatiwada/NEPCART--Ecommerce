from django.contrib import admin
from .models import Product
from store.models import Variation


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 2


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'initial_price', 'price', 'stock', 'catogery', 'is_popular', 'is_featured', 'is_available')
    list_editable = ('initial_price', 'price', 'stock', 'is_popular', 'is_featured', 'is_available')
    search_fields = ('product_name', 'description')
    list_filter = ('catogery', 'is_popular', 'is_featured', 'is_available')
    inlines = [VariationInline]


admin.site.register(Product, ProductAdmin)
