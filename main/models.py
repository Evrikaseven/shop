from django.db import models


# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    vk_link = models.CharField(max_length=256, null=True, blank=True)
    space = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    picture = models.CharField(max_length=256, null=True, blank=True)
    product_type = models.CharField(max_length=256, null=True, blank=True)

