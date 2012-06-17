from django.contrib.admin.sites import site
from recipes.models import Recipe

site.register(Recipe)
