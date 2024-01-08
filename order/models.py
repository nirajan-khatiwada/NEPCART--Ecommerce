from django.db import models
from account.models import Account


class OrderAddress(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    city = models.CharField(max_length=50)

    def full_address(self):
        return f"{self.address_line_1}, {self.city}, {self.state}, {self.country}"

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.state}, {self.country}"


class Order(models.Model):
    STATUS = (
        ('Paid', 'Paid'),
        ('Deliverred', 'Delivered'),
        ('Cancaled', 'Cancaled'),
        ('Ongoing', 'Ongoing')
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    order_number = models.AutoField(primary_key=True)
    Address = models.ForeignKey(OrderAddress, on_delete=models.CASCADE, null=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='Paid')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.user}"
