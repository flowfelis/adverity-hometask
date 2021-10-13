from django.db import models


class Collection(models.Model):
    filename = models.CharField(max_length=256)
    date_added = models.DateTimeField(auto_now_add=True)
