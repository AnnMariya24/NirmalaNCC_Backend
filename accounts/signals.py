from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def send_approval_email(sender, instance, created, **kwargs):
    # If user is updated (not created) and approved
    if not created and instance.is_approved:
        send_mail(
            subject="NCC Registration Approved",
            message=f"""
Hello {instance.name},

Your NCC registration has been approved.

You can now login to the system.

Regards,
Nirmala NCC
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.email],
            fail_silently=True,
        )