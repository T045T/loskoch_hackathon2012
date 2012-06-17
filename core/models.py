import random
from string import letters, digits

from django.db import models
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from django.contrib.gis.db.models import PointField, GeoManager

from django_facebook.models import FacebookProfileModel



def generate_flatshare_token():
    return ''.join(random.choice(letters + digits) for _ in xrange(20))


class Flatshare(models.Model):
    token = models.CharField(max_length=20, default=generate_flatshare_token)
    admin = models.ForeignKey(User)
    name = models.CharField(max_length=50, blank=True, null=True)
    size = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField(validators=[MinValueValidator(2)])
    address = models.CharField(max_length=200)
    location = PointField()

    latest_pairing = models.ForeignKey('pairings.Pairing',
        blank=True, null=True)

    objects = GeoManager()

    def __unicode__(self):
        return unicode(self.id)


class PersonProfile(FacebookProfileModel):
    user = models.OneToOneField(User)
    flat = models.ForeignKey(Flatshare, null=True, related_name='flatmates')

    def get_start_time_candidates_for_latest_pairing(self):
        return self.flat.latest_pairing.start_time_candidates.filter(
            user=self.user)

    def has_entered_schedule_for_latest_pairing(self):
        return self.get_start_time_candidates_for_latest_pairing().exclude(
            time=None).exists()

    def can_vote_on_current_pairing(self):
        return self.flat.latest_pairing.all_votes.filter(voter=self.user).count() < 3

    def count_votes_left(self):
        if self.can_vote_on_current_pairing():
            return 3 - self.flat.latest_pairing.votes.filter(
                user=self.user).count()
        else:
            return 0

    def vote(self, recipe):
        from recipes.models import Vote
        if self.can_vote_on_current_pairing():
            Vote.objects.create(
                voter=self.user,
                vote_recipe=recipe,
                my_pairing=self.flat.latest_pairing)


def create_facebook_profile(sender, instance, created, **kwargs):
    if created:
        PersonProfile.objects.create(user=instance)


def post_create_flatshare(sender, instance, created, **kwargs):
    if created:
        from pairings.models import generate_pairing
        generate_pairing(instance)

post_save.connect(create_facebook_profile, sender=User)
post_save.connect(post_create_flatshare, sender=Flatshare)
