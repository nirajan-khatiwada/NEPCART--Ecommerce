from django.db import models
from django.utils.text import slugify
# Create your models here.
class category(models.Model):
    category_name=models.CharField(max_length=50,unique=True,null=False,blank=False)
    slug=models.SlugField(db_index=True,null=False,unique=True,blank=True,editable=False)
    description=models.CharField(max_length=50,blank=True)
    category_image=models.ImageField(upload_to="images/category")
    def __str__(self):
        return self.category_name
    def save(self,*args,**kwargs):
        self.slug=slugify(self.category_name)
        super().save(*args,**kwargs)
    

