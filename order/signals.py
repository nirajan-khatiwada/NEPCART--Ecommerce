from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order


@receiver(pre_save, sender=Order)
def track_previous_status(sender, instance, **kwargs):
    """Tracks previous status before saving to detect status changes."""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def send_order_status_email(sender, instance, created, **kwargs):
    """Dispatches status update email notification to user when order status changes."""
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status

    # Do not send duplicate email on initial creation (handled by invoice email in views.py) or if status did not change
    if created or old_status == new_status:
        return

    if not instance.user or not instance.user.email:
        return

    subject_map = {
        'Paid': f"Nepcart Payment Confirmation - Order #{instance.order_number}",
        'Ongoing': f"Nepcart Order On The Way - Order #{instance.order_number}",
        'Deliverred': f"Nepcart Order Delivered - Order #{instance.order_number}",
        'Cancaled': f"Nepcart Order Canceled - Order #{instance.order_number}",
    }

    subject = subject_map.get(new_status, f"Nepcart Order Status Update - Order #{instance.order_number}")

    context = {
        'order': instance,
        'user': instance.user,
        'status': new_status,
        'order_items': instance.order_items.all(),
        'address': instance.Address,
    }

    try:
        html_content = render_to_string("order/status_email.html", context)
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Your Nepcart Order #{instance.order_number} status is now: {new_status}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
    except Exception as e:
        print(f"Failed to send status notification email: {e}")
