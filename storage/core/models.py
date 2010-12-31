from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from utils import ChoiceBase


class Direction(ChoiceBase):
        IN = 'In'
        OUT = 'Out'


class VirtualEntry(models.Model):
        user = models.ForeignKey(User)
        date = models.DateTimeField()

        
class Entry(VirtualEntry):
        direction=models.CharField(choices = Direction.Choices())

      