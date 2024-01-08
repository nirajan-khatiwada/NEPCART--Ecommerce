import requests
from uuid import uuid4
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from cart.models import CartItem
from cart.views import get_coupon_discount
from .models import Order, OrderAddress
from . import forms


def get_khalti_headers():
    """Format authorization header per Khalti v2 API specification: Authorization: Key <SECRET_KEY>"""
    key = settings.KHALTI_SECRET_KEY.strip()
    if not (key.startswith("Key ") or key.startswith("key ")):
        auth_header = f"Key {key}"
    else:
        secret_part = key.split(' ', 1)[-1]
        auth_header = f"Key {secret_part}"
        
    return {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }


@login_required(login_url="login")
def payment(request):
    """Initiates Khalti ePayment v2 flow with promo code discount applied."""
    if request.method != "POST":
        return redirect(reverse("placeorder"))

    orderaddr = OrderAddress.objects.filter(user=request.user).order_by('-id').first()
    if not orderaddr:
        form = forms.OrderForm(request.POST)
        if form.is_valid():
            orderaddr, _ = OrderAddress.objects.get_or_create(
                user=request.user,
                country=form.cleaned_data.get('country'),
                state=form.cleaned_data.get('state'),
                address_line_1=form.cleaned_data.get('address_line_1'),
                city=form.cleaned_data.get('city'),
            )
        else:
            messages.error(request, "Delivery address missing. Please set up your delivery info in your profile first.")
            return redirect(reverse("placeorder"))

    cart_items = CartItem.objects.filter(user=request.user, is_ordered=False)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect(reverse("cart"))

    # Amount calculations (in NPR and Paisa) with promo code discount applied
    total = sum(item.subtotal() for item in cart_items)
    tax = round(0.13 * total, 2)
    coupon, discount = get_coupon_discount(request, total)
    grandtotal = max(0, round(total + tax - discount, 2))

    amount_in_paisa = int(round(grandtotal * 100))
    tax_in_paisa = int(round(tax * 100))
    subtotal_in_paisa = amount_in_paisa - tax_in_paisa  # Ensure exact breakdown sum equality

    host = f'http://{request.META.get("HTTP_HOST", "localhost:8000")}'
    initiate_url = f"{settings.KHALTI_BASE_URL.rstrip('/')}/initiate/"

    customer_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    phone_number = getattr(request.user, 'phone_number', '9800000000') or '9800000000'

    # Build product_details list per Khalti v2 documentation specifications
    product_details = []
    for item in cart_items:
        unit_paisa = int(round(item.product.price * 100))
        subtotal_paisa = int(round(item.subtotal() * 100))
        product_details.append({
            "identity": str(item.product.id),
            "name": str(item.product.product_name),
            "total_price": subtotal_paisa,
            "quantity": item.quantity,
            "unit_price": unit_paisa
        })

    subtotal_label = "Subtotal"
    if coupon and discount > 0:
        subtotal_label = f"Subtotal ({coupon.discount_percent}% OFF Applied)"

    payload = {
        "return_url": f'{host}{reverse("verify")}',
        "website_url": f"{host}/",
        "amount": amount_in_paisa,
        "purchase_order_id": str(uuid4()),
        "purchase_order_name": f"Nepcart Order ({cart_items.count()} item{'s' if cart_items.count() > 1 else ''})",
        "customer_info": {
            "name": customer_name,
            "email": request.user.email or "test@khalti.com",
            "phone": str(phone_number),
        },
        "amount_breakdown": [
            {"label": subtotal_label, "amount": subtotal_in_paisa},
            {"label": "VAT (13%)", "amount": tax_in_paisa}
        ],
        "product_details": product_details
    }

    try:
        response = requests.post(initiate_url, json=payload, headers=get_khalti_headers(), timeout=15)
        res = response.json()

        if response.status_code == 200 and 'payment_url' in res:
            return redirect(res['payment_url'])
        else:
            error_msg = res.get('detail') or res.get('message') or str(res)
            messages.error(request, f"Khalti Error: {error_msg}")
            return redirect(reverse("placeorder"))
    except Exception as e:
        messages.error(request, "Failed to connect to Khalti payment gateway.")
        return redirect(reverse("placeorder"))


@login_required(login_url="login")
def verify(request):
    """Verifies Khalti payment status via lookup API and GET callback parameters."""
    pidx = request.GET.get("pidx")
    if not pidx:
        messages.error(request, "Payment reference (pidx) missing.")
        return redirect(reverse("placeorder"))

    status = request.GET.get("status")
    total_amount_get = request.GET.get("total_amount")

    lookup_url = f"{settings.KHALTI_BASE_URL.rstrip('/')}/lookup/"
    payload = {"pidx": pidx}

    paid_amount_paisa = 0
    is_completed = False

    try:
        response = requests.post(lookup_url, json=payload, headers=get_khalti_headers(), timeout=15)
        if response.status_code == 200:
            res = response.json()
            status = res.get("status") or status
            paid_amount_paisa = res.get("total_amount") or total_amount_get or 0
        else:
            paid_amount_paisa = total_amount_get or 0
    except Exception as e:
        print("Khalti lookup Exception:", e)
        paid_amount_paisa = total_amount_get or 0

    is_completed = (str(status).strip().lower() == "completed")

    if is_completed:
        cart_items = CartItem.objects.filter(user=request.user, is_ordered=False)
        if not cart_items.exists():
            messages.warning(request, "Payment verified, but cart items were already processed.")
            return redirect(reverse("dashbord"))

        total = sum(item.subtotal() for item in cart_items)
        tax = round(0.13 * total, 2)
        coupon, discount = get_coupon_discount(request, total)
        grandtotal = max(0, round(total + tax - discount, 2))
        expected_amount_paisa = int(round(grandtotal * 100))

        try:
            paid_amount_int = int(paid_amount_paisa)
        except (ValueError, TypeError):
            paid_amount_int = 0

        # Match integer paid amount with expected grandtotal in paisa
        if paid_amount_int == expected_amount_paisa or paid_amount_int == int(round((total + tax) * 100)):
            orderaddr = OrderAddress.objects.filter(user=request.user).last()

            # Save finalized Order record
            new_order = Order.objects.create(
                user=request.user,
                Address=orderaddr,
                order_total=grandtotal,
                tax=tax,
                status="Paid"
            )

            # Deduct inventory stock & mark cart items as ordered BEFORE sending email
            ordered_items = list(cart_items)
            for item in ordered_items:
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save()
                item.is_ordered = True
                item.order = new_order
                item.save()

            # Clear promo code from session after successful order
            request.session.pop('coupon_code', None)

            # Send invoice email with full order details & items
            email_context = {
                'order': orderaddr,
                'order_obj': new_order,
                'order_items': ordered_items,
                'total': total,
                'tax': tax,
                'discount': discount,
                'coupon': coupon,
                'grandtotal': grandtotal,
                'status': 'Paid',
                'request': request
            }
            try:
                html_data = render_to_string("order/order_complete.html", email_context)
                email = EmailMultiAlternatives(
                    f"Invoice & Payment Confirmation - Order #{new_order.order_number}",
                    f"Order #{new_order.order_number} Invoice Detail",
                    settings.DEFAULT_FROM_EMAIL,
                    to=[request.user.email]
                )
                email.attach_alternative(html_data, 'text/html')
                email.send(fail_silently=True)
            except Exception as e:
                print("Failed to send order invoice email:", e)

            messages.success(request, f"Payment Successful! Your order #{new_order.order_number} for NPR {grandtotal} has been paid and confirmed.")
            return redirect("order")
        else:
            messages.error(request, f"Payment amount mismatch. Paid: NPR {paid_amount_int/100}, Expected: NPR {expected_amount_paisa/100}")
            return redirect(reverse("cart"))
    else:
        messages.error(request, f"Payment status: {status or 'Failed'}. Transaction was not completed.")
        return redirect(reverse("placeorder"))