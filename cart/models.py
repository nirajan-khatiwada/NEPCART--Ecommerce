from django.db import models
from product.models import Product
from store.models import Variation
from account.models import Account


class Cart(models.Model):
    cart_id = models.CharField(max_length=50)
    date = models.DateField(auto_auto_now=True) if hasattr(models, 'auto_auto_now') else models.DateField(auto_now=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="user", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="carts", null=True, blank=True)
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, null=True, blank=True, related_name="order_items")
    quantity = models.IntegerField()
    is_ordered = models.BooleanField(default=False)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Promo code text (e.g. NEPCART10)")
    discount_percent = models.IntegerField(help_text="Percentage discount (e.g. 10 for 10% OFF)")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.discount_percent}% OFF"