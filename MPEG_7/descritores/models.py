from django.db import models

# Create your models here.

class ImageModel(models.Model):
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=200)
    color_layout_y = models.JSONField()
    color_layout_cb = models.JSONField()
    color_layout_cr = models.JSONField()    
    edge_histogram = models.JSONField()

    def __str__(self):
        return self.name