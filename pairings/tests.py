from django.test import TestCase
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from django.utils.timezone import now

from core.models import Flatshare
from pairings.models import generate_pairings, Pairing


def make_flat(**kwargs):
    # Disable auto generation of pairings for tests
    import pairings.models
    _old_generate_pairings = pairings.models.generate_pairings
    pairings.models.generate_pairings = lambda *foo: None

    flat = Flatshare.objects.create(admin_id=0, **kwargs)
    for i in range(kwargs['size']):
        user = User.objects.create_user(username='%d-%d' % (flat.id, i), password='a')
        user.get_profile().flat = flat
        user.get_profile().save()

    pairings.models.generate_pairings = _old_generate_pairings

    return flat


class PairingGeneratorTests(TestCase):
    def test_1(self):
        flat1 = make_flat(size=3, max_guests=5, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=4, max_guests=5, location=Point(49.011078, 8.416171))
        self.assertGeneratesPairing(flat1, flat2)

    def test_max_guests_too_small(self):
        flat1 = make_flat(size=3, max_guests=2, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=4, max_guests=2, location=Point(49.011078, 8.416171))
        self.assertGeneratesPairing(flat1, None)

    def test_too_big(self):
        flat1 = make_flat(size=2, max_guests=5, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=4, max_guests=5, location=Point(49.011078, 8.416171))
        self.assertGeneratesPairing(flat1, None)


    def test_only_undated(self):
        flat1 = make_flat(size=4, max_guests=5, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=4, max_guests=4, location=Point(49.011078, 8.416171))

        self.assertGeneratesPairing(flat1, flat2)
        self.assertGeneratesPairing(flat1, None)

    def test_only_free(self):
        flat1 = make_flat(size=4, max_guests=3, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=3, max_guests=5, location=Point(49.011078, 8.416171))

        self.assertGeneratesPairing(flat1, flat2)
        p1 = Pairing.objects.get()
        p1.start_datetime = now()
        p1.save()

        flat3 = make_flat(size=5, max_guests=3, location=Point(49.011058, 8.416151))
        self.assertGeneratesPairing(flat3, None)

        Flatshare.objects.update(latest_pairing=None)
        self.assertGeneratesPairing(flat3, flat2)

    def assertGeneratesPairing(self, host, guest):
        old_pks = [p.pk for p in Pairing.objects.all()]
        generate_pairings()
        try:
            pairing = Pairing.objects.exclude(pk__in=old_pks).get()
            self.assertEqual(set(pairing.flats.all()), set([host, guest]))
        except Pairing.DoesNotExist:
            if guest is not None:
                self.fail("no pairing generated but expected %s" % [host, guest])
