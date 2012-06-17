from django.contrib.admin.sites import site

from pairings.models import Pairing, StartTimeCandidate

for model in [Pairing, StartTimeCandidate]:
    site.register(model)
