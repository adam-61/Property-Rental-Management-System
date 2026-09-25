from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('owner', 'Property Owner'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant', verbose_name="Account Role")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Bio / About Me")
    location = models.CharField(max_length=100, blank=True, verbose_name="Location")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    avatar = models.ImageField(upload_to='profile_pics', blank=True, null=True, verbose_name="Profile Picture")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_owner(self):
        return self.role == 'owner'

    @property
    def is_tenant(self):
        return self.role == 'tenant'

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
