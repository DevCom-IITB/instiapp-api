"""Model for AlumniUser."""
from __future__ import unicode_literals
import hashlib
import re
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import time

class AlumniUser(models.Model):
    """Profile for Alumni Login Requests."""
    ldap = models.CharField(max_length=30)
    keyStored = models.CharField(max_length=6, null = True, blank = True)
    timeLoginRequest = models.DateTimeField()

    def __str__(self):
        return self.ldap

    def isCorrectKey(self, keyEntered):
        return keyEntered == self.keyStored