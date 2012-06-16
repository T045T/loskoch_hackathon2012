import random
from string import letters, digits

from django.db import models
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from django.contrib.gis.db.models import PointField

from django_facebook.models import FacebookProfileModel


def generate_flatshare_token():
    return ''.join(random.choice(letters+digits) for _ in xrange(20))


class Flatshare(models.Model):
    token = models.CharField(max_length=20, default=generate_flatshare_token,
                             editable=False)
    admin = models.ForeignKey(User, editable=False)
    name = models.CharField(max_length=50, blank=True, null=True)
    size = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField(validators=[MinValueValidator(2)])
    address = models.CharField(max_length=200)
    location = PointField()


class PersonProfile(FacebookProfileModel):
    user = models.OneToOneField(User)
    flat = models.ForeignKey(Flatshare, null=True, related_name='flatmates')


def create_facebook_profile(sender, instance, created, **kwargs):
    if created:
        PersonProfile.objects.create(user=instance)

post_save.connect(create_facebook_profile, sender=User)
