from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    synopsis = models.TextField(blank=True)
    duration = models.DecimalField(max_digits=10, decimal_places=0)
