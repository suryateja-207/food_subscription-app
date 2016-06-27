from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey
from datetime import datetime
from django.db import models


class FoodSubscription(models.Model):
    user = models.ForeignKey(User, null=True)
    date = models.DateField(default=datetime.now, blank=True)
    is_eating = models.BooleanField(default=False)
    class Meta:
       verbose_name = "FoodSubscription"
       verbose_name_plural = "FoodSubscription"
