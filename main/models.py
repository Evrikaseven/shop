from django.db import models


# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=256)
    space = models.CharField(max_length=150)

