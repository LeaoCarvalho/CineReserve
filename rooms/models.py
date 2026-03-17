from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    number_seats = models.PositiveIntegerField(null=False)
