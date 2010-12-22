from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Profile(models.Model):
        user = models.ForeignKey(User)
        barcode = models.TextField()
        active = models.BooleanField(default = True)

def create_user_profile(sender, instance, created, **kwargs):
        if created:
                profile, created = Profile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=django.contrib.auth.models.User)
      