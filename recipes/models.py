from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Recipe(models.Model):
    owner = models.ForeignKey(User, editable=False, related_name='recipes')
    name = models.CharField(max_length=50, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    image_url = models.URLField()
