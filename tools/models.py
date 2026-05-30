from django.db import models

class ImageProcess(models.Model):
    original_image = models.ImageField(upload_to='original/')
    processed_image = models.ImageField(upload_to='processed/', null=True, blank=True)

    original_size = models.FloatField(null=True, blank=True)
    compressed_size = models.FloatField(null=True, blank=True)
    compression_percentage = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)