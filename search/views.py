from django.shortcuts import render
from category.models import category
from product.models import Product
from django.db.models import Q
# Create your views here.
def search(request):
    search=request.GET.get('search')
    product = Product.objects.filter(Q(product_name__icontains=search) | Q(description__contains=search))
    return render(request,"search/search-result.html",{'data':product,'len_product':len(product),'catogery':category.objects.all()})