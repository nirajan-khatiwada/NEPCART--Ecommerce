import os
import urllib.request
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from django.core.files.base import ContentFile
from django.utils.text import slugify
from category.models import category
from product.models import Product
from store.models import Variation
from cart.models import CartItem, Cart
from order.models import Order, OrderAddress

def seed_data():
    print("Clearing old data...")
    CartItem.objects.all().delete()
    Cart.objects.all().delete()
    Order.objects.all().delete()
    OrderAddress.objects.all().delete()
    Variation.objects.all().delete()
    Product.objects.all().delete()
    category.objects.all().delete()

    print("Creating categories...")
    cat_data = [
        {"name": "Shirt", "desc": "Men & Women Fashion Shirts", "url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&auto=format&fit=crop&q=80"},
        {"name": "Jacket", "desc": "Warm & Stylish Jackets", "url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop&q=80"},
        {"name": "Sofa", "desc": "Living Room Furniture Sofas", "url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&auto=format&fit=crop&q=80"},
        {"name": "Watch", "desc": "Smart & Classic Watches", "url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=80"},
        {"name": "Airpod", "desc": "Wireless Earbuds & Headphones", "url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&auto=format&fit=crop&q=80"},
        {"name": "Bag", "desc": "Backpacks & Travel Bags", "url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop&q=80"},
        {"name": "Shoes", "desc": "Sneakers & Formal Footwear", "url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=80"},
        {"name": "Electronics", "desc": "Keyboards, Mice & Accessories", "url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&auto=format&fit=crop&q=80"}
    ]

    cat_map = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    for c in cat_data:
        cat_obj = category(category_name=c['name'], description=c['desc'])
        req = urllib.request.Request(c['url'], headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                img_data = resp.read()
                cat_obj.category_image.save(f"{slugify(c['name'])}.jpg", ContentFile(img_data), save=False)
        except Exception as e:
            print(f"Error fetching category image {c['name']}: {e}")
        cat_obj.save()
        cat_map[c['name']] = cat_obj

    print("Creating products...")
    products_list = [
        # Shirts
        {
            "name": "Slim Fit Cotton Casual Shirt",
            "cat": "Shirt",
            "desc": "100% breathable pure cotton slim fit casual shirt for everyday comfort.",
            "initial_price": 2500,
            "price": 1800,
            "stock": 25,
            "is_popular": True,
            "is_featured": False,
            "colors": ["White", "Blue", "Black"],
            "sizes": ["S", "M", "L", "XL"],
            "url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Premium Denim Chambray Shirt",
            "cat": "Shirt",
            "desc": "Durable vintage denim chambray shirt with double chest pockets.",
            "initial_price": 3200,
            "price": 2400,
            "stock": 18,
            "is_popular": False,
            "is_featured": True,
            "colors": ["Blue", "Dark Blue"],
            "sizes": ["M", "L", "XL"],
            "url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Classic Plaid Flannel Shirt",
            "cat": "Shirt",
            "desc": "Soft brushed cotton flannel checkered shirt suitable for winter layered fashion.",
            "initial_price": 2800,
            "price": 1990,
            "stock": 30,
            "is_popular": True,
            "is_featured": False,
            "colors": ["Red", "Green", "Black"],
            "sizes": ["S", "M", "L"],
            "url": "https://images.unsplash.com/photo-1589310243389-96a5483213a8?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Summer Linen Cuban Collar Shirt",
            "cat": "Shirt",
            "desc": "Lightweight Cuban resort collar linen shirt perfect for beach & warm weather.",
            "initial_price": 2200,
            "price": 1500,
            "stock": 12,
            "is_popular": False,
            "is_featured": False,
            "colors": ["White", "Beige"],
            "sizes": ["M", "L"],
            "url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&auto=format&fit=crop&q=80"
        },

        # Jackets
        {
            "name": "Heavyweight Leather Biker Jacket",
            "cat": "Jacket",
            "desc": "Genuine leather motorcycle jacket with asymmetric zip and quilted lining.",
            "initial_price": 8500,
            "price": 6200,
            "stock": 10,
            "is_popular": True,
            "is_featured": True,
            "colors": ["Black", "Brown"],
            "sizes": ["M", "L", "XL"],
            "url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Windproof Waterproof Fleece Jacket",
            "cat": "Jacket",
            "desc": "All-weather thermal fleece lined outdoor jacket with adjustable hood.",
            "initial_price": 4800,
            "price": 3500,
            "stock": 22,
            "is_popular": False,
            "is_featured": False,
            "colors": ["Navy", "Black", "Red"],
            "sizes": ["S", "M", "L", "XL"],
            "url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Urban Puffer Down Jacket",
            "cat": "Jacket",
            "desc": "Insulated lightweight puffer jacket providing extreme cold resistance.",
            "initial_price": 6500,
            "price": 4900,
            "stock": 15,
            "is_popular": True,
            "is_featured": False,
            "colors": ["Black", "Olive"],
            "sizes": ["M", "L"],
            "url": "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop&q=80"
        },

        # Sofas
        {
            "name": "Luxury 3-Seater Velvet Sofa",
            "cat": "Sofa",
            "desc": "Plush royal velvet upholstered 3-seater couch with sturdy hardwood frame.",
            "initial_price": 45000,
            "price": 36500,
            "stock": 5,
            "is_popular": True,
            "is_featured": True,
            "colors": ["Blue", "Grey", "Green"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Modern Wooden L-Shape Corner Sofa",
            "cat": "Sofa",
            "desc": "Spacious sectional L-shaped living room sofa with high-density foam cushions.",
            "initial_price": 62000,
            "price": 49999,
            "stock": 3,
            "is_popular": False,
            "is_featured": True,
            "colors": ["Brown", "Beige"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Minimalist Recliner Leather Couch",
            "cat": "Sofa",
            "desc": "Ergonomic leather recliner armchair with smooth push-back mechanism.",
            "initial_price": 38000,
            "price": 29900,
            "stock": 8,
            "is_popular": False,
            "is_featured": False,
            "colors": ["Black", "Tan"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=600&auto=format&fit=crop&q=80"
        },

        # Watches
        {
            "name": "Full Fletched ScreenTouch Smartwatch",
            "cat": "Watch",
            "desc": "HD touch display smartwatch with heart rate, blood oxygen & fitness tracking.",
            "initial_price": 1200,
            "price": 699,
            "stock": 40,
            "is_popular": True,
            "is_featured": True,
            "colors": ["Black", "Silver"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Classic Chronograph Stainless Steel Watch",
            "cat": "Watch",
            "desc": "Water-resistant quartz movement luxury chronograph watch for men.",
            "initial_price": 7500,
            "price": 5400,
            "stock": 14,
            "is_popular": False,
            "is_featured": True,
            "colors": ["Silver", "Gold", "Black"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Minimalist Leather Quartz Dress Watch",
            "cat": "Watch",
            "desc": "Ultra-thin analog wrist watch with genuine Italian leather strap.",
            "initial_price": 4800,
            "price": 3600,
            "stock": 20,
            "is_popular": True,
            "is_featured": False,
            "colors": ["Brown", "Black"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=600&auto=format&fit=crop&q=80"
        },

        # Airpods & Audio
        {
            "name": "Best Gaming Noise-Canceling Earpods",
            "cat": "Airpod",
            "desc": "Low latency gaming wireless earpods with active noise cancellation & RGB case.",
            "initial_price": 890,
            "price": 399,
            "stock": 60,
            "is_popular": True,
            "is_featured": True,
            "colors": ["Black", "White"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Pro Wireless Bluetooth Earbuds",
            "cat": "Airpod",
            "desc": "High definition stereo sound earbuds with wireless charging case & mic.",
            "initial_price": 4500,
            "price": 3200,
            "stock": 35,
            "is_popular": False,
            "is_featured": True,
            "colors": ["White", "Black"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Studio Over-Ear Wireless Headphones",
            "cat": "Airpod",
            "desc": "Deep bass over-ear wireless Bluetooth headphones with 40-hour battery life.",
            "initial_price": 8900,
            "price": 6500,
            "stock": 16,
            "is_popular": True,
            "is_featured": False,
            "colors": ["Black", "Silver"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80"
        },

        # Bags
        {
            "name": "A Big Giant Travel Backpack",
            "cat": "Bag",
            "desc": "Heavy-duty 45L expandable trekking & laptop backpack with USB charging port.",
            "initial_price": 1200,
            "price": 699,
            "stock": 25,
            "is_popular": True,
            "is_featured": False,
            "colors": ["Black", "Navy"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Waterproof Executive Laptop Bag",
            "cat": "Bag",
            "desc": "Sleek professional business laptop backpack fitting up to 15.6 inch laptops.",
            "initial_price": 3800,
            "price": 2700,
            "stock": 30,
            "is_popular": False,
            "is_featured": True,
            "colors": ["Grey", "Black"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Genuine Leather Messenger Crossbody Bag",
            "cat": "Bag",
            "desc": "Vintage handcrafted real leather shoulder bag for work and travel.",
            "initial_price": 5500,
            "price": 3990,
            "stock": 15,
            "is_popular": True,
            "is_featured": False,
            "colors": ["Brown", "Tan"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&auto=format&fit=crop&q=80"
        },

        # Shoes
        {
            "name": "Breathable Lightweight Running Sneakers",
            "cat": "Shoes",
            "desc": "Cushioned shock-absorbing sports running shoes for gym and daily wear.",
            "initial_price": 4200,
            "price": 2900,
            "stock": 28,
            "is_popular": True,
            "is_featured": True,
            "colors": ["Black", "White", "Red"],
            "sizes": ["39", "40", "41", "42", "43"],
            "url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Classic Leather Formal Oxford Shoes",
            "cat": "Shoes",
            "desc": "Polished patent leather lace-up formal dress shoes for business attire.",
            "initial_price": 6800,
            "price": 4950,
            "stock": 14,
            "is_popular": False,
            "is_featured": True,
            "colors": ["Black", "Brown"],
            "sizes": ["40", "41", "42"],
            "url": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "High-Top Outdoor Trekking Boots",
            "cat": "Shoes",
            "desc": "Rugged anti-slip waterproof hiking boots designed for Nepal trekking trails.",
            "initial_price": 7500,
            "price": 5600,
            "stock": 18,
            "is_popular": True,
            "is_featured": False,
            "colors": ["Tan", "Olive"],
            "sizes": ["41", "42", "43"],
            "url": "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=600&auto=format&fit=crop&q=80"
        },

        # Electronics
        {
            "name": "RGB Mechanical Gaming Keyboard",
            "cat": "Electronics",
            "desc": "Custom tactile mechanical switches keyboard with customizable per-key RGB backlighting.",
            "initial_price": 5200,
            "price": 3800,
            "stock": 24,
            "is_popular": True,
            "is_featured": True,
            "colors": ["Black", "White"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80"
        },
        {
            "name": "Ergonomic Optical Wireless Gaming Mouse",
            "cat": "Electronics",
            "desc": "High precision 16,000 DPI sensor wireless gaming mouse with programmable buttons.",
            "initial_price": 2800,
            "price": 1900,
            "stock": 35,
            "is_popular": False,
            "is_featured": True,
            "colors": ["Black"],
            "sizes": [],
            "url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80"
        }
    ]

    for p in products_list:
        cat_obj = cat_map[p['cat']]
        prod_obj = Product(
            product_name=p['name'],
            description=p['desc'],
            initial_price=p['initial_price'],
            price=p['price'],
            stock=p['stock'],
            is_available=True,
            is_popular=p['is_popular'],
            is_featured=p['is_featured'],
            catogery=cat_obj
        )

        req = urllib.request.Request(p['url'], headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                img_data = resp.read()
                prod_obj.image.save(f"{slugify(p['name'])}.jpg", ContentFile(img_data), save=False)
        except Exception as e:
            print(f"Error fetching image for {p['name']}: {e}")

        prod_obj.save()

        # Add Color variations
        for col in p.get('colors', []):
            Variation.objects.create(
                product=prod_obj,
                variation_category='color',
                variation_value=col,
                is_active=True
            )

        # Add Size variations
        for sz in p.get('sizes', []):
            Variation.objects.create(
                product=prod_obj,
                variation_category='size',
                variation_value=sz,
                is_active=True
            )

        print(f"Added product: {prod_obj.product_name} (NPR {prod_obj.price})")

    print("Data seeding completed successfully! Total products created:", Product.objects.count())

if __name__ == "__main__":
    seed_data()
