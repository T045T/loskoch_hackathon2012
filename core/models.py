from django.db import models
from django.core.validators import MinValueValidator


class Flatshare(models.Model):
    # TODO geo coordinates
    address = models.TextField()
    max_guests = models.PositiveIntegerField(validators=[MinValueValidator(2)])


class UserProfile(models.Model):
    year_of_birth = models.PositiveIntegerField()
