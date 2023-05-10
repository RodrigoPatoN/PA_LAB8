from django.db import models

# Create your models here.

class ImageModel(models.Model):
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=200)
    color_layout = models.JSONField()
    edge_histogram = models.JSONField()

class ImageInserted(models.Model):
    image = models.ImageField()