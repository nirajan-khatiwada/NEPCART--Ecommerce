from django.contrib import admin
from .models import Order, OrderAddress
from cart.models import CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'get_variations', 'quantity', 'get_subtotal')
    fields = ('product', 'get_variations', 'quantity', 'get_subtotal')
    can_delete = False

    def get_variations(self, obj):
        if obj.variations.exists():
            return ", ".join([f"{v.variation_category}: {v.variation_value}" for v in obj.variations.all()])
        return "No size & color"
    get_variations.short_description = "Selected Variations"

    def get_subtotal(self, obj):
        return f"NPR {obj.subtotal()}"
    get_subtotal.short_description = "Subtotal"


class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address_line_1', 'city', 'state', 'country')
    search_fields = ('user__username', 'address_line_1', 'city', 'state', 'country')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'full_delivery_address', 'status', 'order_total', 'tax', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'Address__address_line_1', 'Address__city', 'Address__state', 'Address__country')
    list_editable = ('status',)
    readonly_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone', 'full_delivery_address', 'created_at')
    inlines = [CartItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'created_at', 'order_total', 'tax')
        }),
        ('Customer Details', {
            'fields': ('user', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping & Delivery Address', {
            'fields': ('Address', 'full_delivery_address')
        }),
    )

    def customer_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return "N/A"
    customer_name.short_description = "Customer Name"

    def customer_email(self, obj):
        if obj.user:
            return obj.user.email
        return "N/A"
    customer_email.short_description = "Customer Email"

    def customer_phone(self, obj):
        if obj.user:
            return getattr(obj.user, 'phone_number', 'N/A') or "N/A"
        return "N/A"
    customer_phone.short_description = "Customer Phone"

    def full_delivery_address(self, obj):
        if obj.Address:
            return f"{obj.Address.address_line_1}, {obj.Address.city}, {obj.Address.state}, {obj.Address.country}"
        return "No address specified"

    full_delivery_address.short_description = "Full Delivery Address"


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderAddress, OrderAddressAdmin)
