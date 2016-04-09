from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models


class User(models.Model):
    username = models.CharField(unique=True, max_length=100)
    session = models.CharField(unique=True, max_length=255)
    expired = models.NullBooleanField()
    
    