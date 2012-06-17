from django.utils.timezone import now, timedelta
import math
import urllib
from itertools import chain
from django.db import models
from core.models import Flatshare


Q = models.Q


class Pairing(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    host = models.ForeignKey(Flatshare, related_name='hosted_pairings')
    flats = models.ManyToManyField(Flatshare, related_name='pairings')
    start_datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created']

    def all_recipes(self):
        all_recipes = []
        for flat in self.flats.all():
            for mate in flat.flatmates.all():
                for recipe in mate.user.recipes.all():
                    all_recipes.append(recipe)
                    recipe.votes = self.all_votes.filter(vote_recipe=recipe).count()
        return all_recipes

    def gmaps_url(self, guest):
        url = 'https://maps.google.com/maps?'
        values = {'saddr': guest.address.encode("utf-8"), 'daddr': self.host.address.encode("utf-8")}
        return url + urllib.urlencode(values)

    def get_all_flatmates(self):
        mates = []
        for flat in self.flats.all():
            mates.extend(flat.flatmates.all())
        return mates


class StartTimeCandidate(models.Model):
    pairing = models.ForeignKey(Pairing, related_name='start_time_candidates')
    user = models.ForeignKey('auth.User')
    day = models.DateField()
    time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['day']


RANDOM = '?'


def generate_pairings():
    # Exclude flats with pending invitations.
    only_complete_flats = Flatshare.objects.annotate(flatmates_count=models.Count('flatmates')) \
                                           .filter(flatmates_count=models.F('size'))

    # Exclude flat shares that are already seeing someone.
    today_minus_ten_days = (now() - timedelta(days=10)).replace(hour=0, minute=0, second=0)
    only_free_flats = Q(latest_pairing=None) | Q(latest_pairing__start_datetime__lte=today_minus_ten_days)

    host_candidates = guest_candidates = only_complete_flats.filter(only_free_flats).order_by('?')
    guest_candidates = guest_candidates.all()

    while 1:
        try:
            host = host_candidates[0]
        except IndexError:
            break
        pairing = generate_pairing(host, guest_candidates)
        if pairing:
            guest_candidates = guest_candidates.exclude(
                pk__in=[flat.pk for flat in pairing.flats.all()])
        host_candidates = host_candidates.exclude(pk=host.pk)


def generate_pairing(host_flat, guest_candidates):
    # TODO: singles

    n_guests_min = math.ceil(0.6 * host_flat.size)
    n_guests_max = min(math.ceil(1.2 * host_flat.size),
                       host_flat.max_guests)

    # Only flat shares that are within 7km distance
    nearby_flats = Q(location__distance_lte=(host_flat.location, 0.09)) # 7km

    # Only flats that are neither too small for everyone to feel comfortable,
    # nor too big to accommodate everyone.
    properly_sized_flats = Q(size__range=[n_guests_min, n_guests_max])

    # Exclude all the flat shares that the host already knows (including itself).
    already_dated_pks = [flat.pk for flat in chain.from_iterable(
                            pairing.flats.all() for pairing in host_flat.pairings.all())]
    only_undated_flats = ~Q(pk__in=already_dated_pks + [host_flat.pk])

    guest_candidates = guest_candidates.filter(nearby_flats) \
                                       .filter(properly_sized_flats) \
                                       .filter(only_undated_flats) \

    try:
        guest_flat = guest_candidates.order_by(RANDOM)[0]
    except IndexError:
        return None

    pairing = Pairing.objects.create(host=host_flat)
    pairing.flats.add(host_flat)
    pairing.flats.add(guest_flat)

    flatmates = list(host_flat.flatmates.all()) + list(guest_flat.flatmates.all())

    for day_offset in range(3, 11):
        day = now().date() + timedelta(days=day_offset)
        for flatmate in flatmates:
            StartTimeCandidate.objects.create(
                pairing=pairing,
                user=flatmate.user,
                day=day,
            )

    host_flat.latest_pairing = pairing
    host_flat.save()

    guest_flat.latest_pairing = pairing
    guest_flat.save()

    return pairing
