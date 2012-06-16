from django.contrib.admin.sites import site

from core.models import Flatshare, PersonProfile

for model in [Flatshare, PersonProfile]:
    site.register(model)
