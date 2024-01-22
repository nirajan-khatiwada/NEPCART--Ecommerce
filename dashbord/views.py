import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from category.models import category
from cart.models import CartItem
from order.models import Order, OrderAddress
from order.forms import OrderForm
from account.models import Account
from .forms import Cpassword


@login_required(login_url="login")
def dashbord(request):
    """User Dashboard view with delivery address editing capability."""
    orderaddr = OrderAddress.objects.filter(user=request.user).order_by("-id").first()

    if request.method == "POST" and request.POST.get('action') == 'update_address':
        address_form = OrderForm(request.POST)
        if address_form.is_valid():
            OrderAddress.objects.create(
                user=request.user,
                country=address_form.cleaned_data['country'],
                state=address_form.cleaned_data['state'],
                address_line_1=address_form.cleaned_data['address_line_1'],
                city=address_form.cleaned_data['city'],
            )
            messages.success(request, "Delivery address saved successfully!")
            return redirect("dashbord")
        else:
            messages.error(request, "Please check delivery address fields.")
    else:
        initial_address = {}
        if orderaddr:
            initial_address = {
                'country': orderaddr.country,
                'state': orderaddr.state,
                'address_line_1': orderaddr.address_line_1,
                'city': orderaddr.city,
            }
        address_form = OrderForm(initial=initial_address)

    user_orders = Order.objects.filter(user=request.user).order_by('-order_number')
    order_count = user_orders.count()
    total_spent = sum(o.order_total for o in user_orders)
    pending_count = user_orders.filter(status__in=['Paid', 'Ongoing', 'New']).count()
    delivered_count = user_orders.filter(status='Deliverred').count()

    context = {
        'catogery': category.objects.all(),
        'order_count': order_count,
        'total_spent': round(total_spent, 2),
        'pending_count': pending_count,
        'delivered_count': delivered_count,
        'orderaddr': orderaddr,
        'address_form': address_form,
        'recent_orders': user_orders[:5],
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required(login_url="login")
def order(request):
    """My Orders view grouped by status (Paid, On Delivery/Ongoing, Delivered, Canceled)."""
    user_orders = Order.objects.filter(user=request.user).order_by('-order_number')
    
    paid_orders = user_orders.filter(status='Paid')
    ongoing_orders = user_orders.filter(status__in=['Ongoing', 'On Delivery', 'New'])
    delivered_orders = user_orders.filter(status='Deliverred')
    canceled_orders = user_orders.filter(status='Cancaled')

    return render(request, "dashboard/order.html", {
        'catogery': category.objects.all(),
        'orders': user_orders,
        'paid_orders': paid_orders,
        'ongoing_orders': ongoing_orders,
        'delivered_orders': delivered_orders,
        'canceled_orders': canceled_orders,
    })



@login_required(login_url="login")
def changepassword(request):
    """Secure Change Password view."""
    form = Cpassword()
    if request.method == "POST":
        form = Cpassword(request.POST)
        if form.is_valid():
            current_pwd = form.cleaned_data['current_password']
            password = form.cleaned_data['password']
            cpassword = form.cleaned_data['cpassword']

            if not request.user.check_password(current_pwd):
                messages.error(request, "Your current password is incorrect.")
            elif password != cpassword:
                messages.error(request, "New password and confirm password do not match.")
            else:
                user = request.user
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)  # Keeps user logged in
                messages.success(request, "Password changed successfully!")
                return redirect("changepassword")

    return render(request, "dashboard/change.html", {
        'catogery': category.objects.all(),
        'form': form
    })
