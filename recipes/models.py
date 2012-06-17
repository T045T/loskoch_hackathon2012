from django.db import models
from django.contrib.auth.models import User
from pairings.models import Pairing


# Create your models here.


class Recipe(models.Model):
    owner = models.ForeignKey(User, editable=False, related_name='recipes')
    name = models.CharField(max_length=50, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    image_url = models.URLField()


class Vote(models.Model):
    voter = models.ForeignKey(User, editable=False, related_name='votes_given')
    vote_recipe = models.ForeignKey(Recipe, editable=False,
        related_name='votes_received')
    my_pairing = models.ForeignKey(Pairing, editable=False,
        related_name='all_votes')
