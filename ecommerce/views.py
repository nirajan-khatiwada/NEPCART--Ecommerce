from django.shortcuts import render
from product.models import Product
from category.models import category


def homepage(request):
    all_products = Product.objects.filter(is_available=True)

    # Filter popular products
    popular_products = all_products.filter(is_popular=True)
    if not popular_products.exists():
        popular_products = all_products[:8]

    # Filter featured products
    featured_products = all_products.filter(is_featured=True)
    if not featured_products.exists():
        featured_products = all_products.order_by('-id')[:8]

    # Group products by category
    categories = category.objects.all()
    category_products = []
    for cat in categories:
        cat_items = all_products.filter(catogery=cat)
        if cat_items.exists():
            category_products.append({
                'category': cat,
                'products': cat_items[:4]
            })

    context = {
        'catogery': categories,
        'popular_products': popular_products,
        'featured_products': featured_products,
        'category_products': category_products,
        'data': all_products
    }
    return render(request, "index.html", context)