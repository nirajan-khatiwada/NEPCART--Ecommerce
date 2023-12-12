from django.shortcuts import render, redirect, get_object_or_404
from product.models import Product
from store.models import Variation
from category.models import category
from .models import Cart, CartItem, Coupon
from django.urls import reverse
from order.forms import OrderForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def get_coupon_discount(request, total):
    """Calculates discount amount from session applied coupon."""
    code = request.session.get('coupon_code')
    if not code:
        return None, 0
    coupon = Coupon.objects.filter(code__iexact=code, active=True).first()
    if not coupon:
        request.session.pop('coupon_code', None)
        return None, 0

    discount = round((total * coupon.discount_percent) / 100, 2)
    return coupon, discount


def apply_coupon(request):
    """Applies promo code to user session."""
    if request.method == "POST":
        code = request.POST.get("coupon_code", "").strip()
        if code:
            coupon = Coupon.objects.filter(code__iexact=code, active=True).first()
            if coupon:
                request.session['coupon_code'] = coupon.code
                messages.success(request, f"Promo Code '{coupon.code}' applied! ({coupon.discount_percent}% OFF)")
            else:
                messages.error(request, "Invalid or expired promo code.")
        else:
            messages.error(request, "Please enter a promo code.")
    return redirect(reverse("cart"))


def remove_coupon(request):
    """Removes promo code from user session."""
    if 'coupon_code' in request.session:
        request.session.pop('coupon_code')
        messages.success(request, "Promo code removed.")
    return redirect(reverse("cart"))


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, product_slug):
    """Adds a product to cart or increments quantity of an existing cart item."""
    product = get_object_or_404(Product, slug=product_slug)
    cart_item_id = request.POST.get('cart_item_id') if request.method == "POST" else None

    # 1. If incrementing quantity from cart page (cart_item_id is provided)
    if cart_item_id:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(id=cart_item_id, user=request.user, is_ordered=False).first()
        else:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item = CartItem.objects.filter(id=cart_item_id, cart=cart, is_ordered=False).first()
            except Cart.DoesNotExist:
                cart_item = None

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
            return redirect(reverse("cart"))

    # 2. If adding from product detail or store page (parse selected variations)
    product_variation = []
    if request.method == "POST":
        for key in request.POST:
            val = request.POST.get(key)
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=val,
                    is_active=True
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    req_var_set = set(product_variation)

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=request.user, is_ordered=False)
        matched_item = None
        for item in cart_items:
            if set(item.variations.all()) == req_var_set:
                matched_item = item
                break

        if matched_item:
            matched_item.quantity += 1
            matched_item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, user=request.user)
            if product_variation:
                item.variations.add(*product_variation)
            item.save()
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        cart_items = CartItem.objects.filter(product=product, cart=cart, is_ordered=False)
        matched_item = None
        for item in cart_items:
            if set(item.variations.all()) == req_var_set:
                matched_item = item
                break

        if matched_item:
            matched_item.quantity += 1
            matched_item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if product_variation:
                item.variations.add(*product_variation)
            item.save()

    return redirect(reverse("cart"))


def remove_cart(request, product_slug):
    cart_item_id = request.POST.get('cart_item_id')
    if request.user.is_authenticated:
        try:
            if cart_item_id:
                cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
            else:
                product = get_object_or_404(Product, slug=product_slug)
                cart_item = CartItem.objects.filter(product=product, user=request.user, is_ordered=False).first()

            if cart_item:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
        except Exception:
            pass
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            if cart_item_id:
                cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
            else:
                product = get_object_or_404(Product, slug=product_slug)
                cart_item = CartItem.objects.filter(product=product, cart=cart, is_ordered=False).first()

            if cart_item:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
        except Exception:
            pass

    return redirect(reverse("cart"))


def delete(request, product_slug):
    cart_item_id = request.POST.get('cart_item_id')
    if request.user.is_authenticated:
        try:
            if cart_item_id:
                CartItem.objects.filter(id=cart_item_id, user=request.user).delete()
            else:
                product = get_object_or_404(Product, slug=product_slug)
                CartItem.objects.filter(product=product, user=request.user, is_ordered=False).delete()
        except Exception:
            pass
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            if cart_item_id:
                CartItem.objects.filter(id=cart_item_id, cart=cart).delete()
            else:
                product = get_object_or_404(Product, slug=product_slug)
                CartItem.objects.filter(product=product, cart=cart, is_ordered=False).delete()
        except Exception:
            pass
    return redirect(reverse("cart"))


def cart(request, total=0, quantity=0, data=None):
    try:
        if request.user.is_authenticated:
            data = CartItem.objects.filter(user=request.user, is_ordered=False)
        else:
            cart_items = Cart.objects.get(cart_id=request.session.session_key)
            data = CartItem.objects.filter(cart=cart_items, is_ordered=False)

        tax = 0
        discount = 0
        grandtotal = 0
        coupon = None

        if data and data.exists():
            for cart_item in data:
                total += cart_item.subtotal()
            tax = round(0.13 * total, 2)
            coupon, discount = get_coupon_discount(request, total)
            grandtotal = max(0, round(total + tax - discount, 2))

        return render(request, "cart/cart.html", {
            'catogery': category.objects.all(),
            'data': data,
            'grandtotal': grandtotal,
            'tax': tax,
            'total': total,
            'coupon': coupon,
            'discount': discount
        })
    except Exception:
        return render(request, "cart/cart.html", {
            'catogery': category.objects.all(),
            'data': None,
            'grandtotal': 0,
            'tax': 0,
            'total': 0,
            'coupon': None,
            'discount': 0
        })


@login_required(login_url="login")
def placeorder(request, total=0, quantity=0):
    data = CartItem.objects.filter(user=request.user, is_ordered=False)
    if not data.exists():
        return redirect(reverse("cart"))

    from order.models import OrderAddress
    saved_address = OrderAddress.objects.filter(user=request.user).order_by('-id').first()
    has_saved_address = False

    if saved_address:
        initial_data = {
            'country': saved_address.country,
            'state': saved_address.state,
            'address_line_1': saved_address.address_line_1,
            'city': saved_address.city,
        }
        form = OrderForm(initial=initial_data)
        has_saved_address = True
    else:
        form = OrderForm()

    try:
        total = sum(item.subtotal() for item in data)
        tax = round(0.13 * total, 2)
        coupon, discount = get_coupon_discount(request, total)
        grandtotal = max(0, round(total + tax - discount, 2))

        return render(request, "cart/place-order.html", {
            'catogery': category.objects.all(),
            'data': data,
            'grandtotal': grandtotal,
            'tax': tax,
            'total': total,
            'form': form,
            'has_saved_address': has_saved_address,
            'saved_address': saved_address,
            'coupon': coupon,
            'discount': discount
        })
    except Exception:
        return render(request, "cart/place-order.html", {
            'catogery': category.objects.all(),
            'data': None,
            'grandtotal': 0,
            'tax': 0,
            'total': 0,
            'form': form,
            'has_saved_address': has_saved_address,
            'saved_address': saved_address,
            'coupon': None,
            'discount': 0
        })