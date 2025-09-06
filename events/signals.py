from django.dispatch import receiver
from django.db.models.signals import post_save
from events.models import RSVP
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=RSVP)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:
        subject = 'New RSVP Added'
        message = f'Hi {instance.user.username},\n\nYou have created a new rsvp for the event {instance.event.name}'
        recipient_list = [instance.user.email]

        try:
            send_mail(subject, message,
                      settings.EMAIL_HOST_USER, recipient_list)
        except Exception as e:
            print(f"Failed to send email to {instance.email}: {str(e)}")
