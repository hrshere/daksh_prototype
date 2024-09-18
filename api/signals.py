from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .views import send_product_notification_to_all_users  # Import your notification function

@receiver(post_save, sender=Product)
def notify_users_product_added(sender, instance, created, **kwargs):
    if created:
        send_product_notification_to_all_users(instance.name)
