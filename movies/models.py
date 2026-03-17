from django.db import models

from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    synopsis = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()

    release_date = models.DateField(null=True, blank=True)
    rating = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.title