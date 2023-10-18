from django.db import models
from category.models import category
from django.utils.text import slugify


class Product(models.Model):
    product_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, blank=True, editable=False)
    description = models.CharField(max_length=250)
    initial_price = models.IntegerField(default=0, help_text="Original price before discount")
    price = models.IntegerField(help_text="Current selling / discounted price")
    image = models.ImageField(upload_to="product/image")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, help_text="Show under Popular Products on landing page")
    is_featured = models.BooleanField(default=False, help_text="Show under Featured Products on landing page")
    catogery = models.ForeignKey(category, on_delete=models.CASCADE, related_name="product")
    created_date = models.DateField(auto_now=True)
    modefied_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        if not self.initial_price or self.initial_price < self.price:
            self.initial_price = self.price
        super().save(*args, **kwargs)
