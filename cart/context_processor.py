from .models import CartItem
def counter(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        data=CartItem.objects.filter(user=request.user,is_ordered=False)
    else:
        if request.session.session_key is None:
            return dict(count=0)
        data=CartItem.objects.filter(cart__cart_id=request.session.session_key)

    quantity=0
    print(data)
    if data:
        for cart in data:
            quantity=quantity+cart.quantity
        return dict(count=quantity)
    else:
        return dict(count=0)
