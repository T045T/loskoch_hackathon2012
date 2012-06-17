from django.test import TestCase
from django.contrib.gis.geos import Point
from django.utils.timezone import now

from core.models import Flatshare
from pairings.models import generate_pairing, Pairing


def make_flat(**kwargs):
    return Flatshare.objects.create(admin_id=0, **kwargs)


class PairingGeneratorTests(TestCase):
    def test_1(self):
        flat1 = make_flat(size=3, max_guests=5, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=4, max_guests=5, location=Point(49.011078, 8.416171))
        self.assertGeneratesPairing(flat1, flat2)

    def test_max_guests_too_small(self):
        flat1 = make_flat(size=3, max_guests=2, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=4, max_guests=5, location=Point(49.011078, 8.416171))
        self.assertGeneratesPairing(flat1, None)

    def test_too_big(self):
        flat1 = make_flat(size=2, max_guests=5, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=4, max_guests=5, location=Point(49.011078, 8.416171))
        self.assertGeneratesPairing(flat1, None)


    def test_only_undated(self):
        flat1 = make_flat(size=3, max_guests=5, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=4, max_guests=5, location=Point(49.011078, 8.416171))
        flat3 = make_flat(size=4, max_guests=5, location=Point(49.011058, 8.416151))

        p1 = Pairing.objects.create(host=flat1)
        p1.flats.add(flat1)
        p1.flats.add(flat2)

        self.assertGeneratesPairing(flat1, flat3)

    def test_only_free(self):
        flat1 = make_flat(size=4, max_guests=3, location=Point(49.009565, 8.403794))
        flat2 = make_flat(size=3, max_guests=5, location=Point(49.011078, 8.416171))
        flat3 = make_flat(size=5, max_guests=3, location=Point(49.011058, 8.416151))

        self.assertGeneratesPairing(flat1, flat2)
        p1 = Pairing.objects.get()
        p1.start_datetime = now()
        p1.save()

        self.assertGeneratesPairing(flat3, None)

        Flatshare.objects.update(latest_pairing=None)
        self.assertGeneratesPairing(flat3, flat2)

    def assertGeneratesPairing(self, host, guest):
        pairing = generate_pairing(host)
        if guest is None:
            self.assertEqual(pairing, None)
        else:
            self.assertEqual(set(pairing.flats.all()), set([host, guest]))
