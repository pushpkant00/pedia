from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return
    first_user = not Profile.objects.exists()
    Profile.objects.create(user=instance,
                           role=Profile.ROLE_ADMIN if first_user else Profile.ROLE_EDITOR)
    if first_user:
        User.objects.filter(pk=instance.pk).update(is_staff=True)
