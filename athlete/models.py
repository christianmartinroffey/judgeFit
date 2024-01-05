from django.db import models


class Athlete(models.Model):
    name = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    age = models.IntegerField(max_length=3)
    email = models.EmailField(max_length=100)
    country = models.ForeignKey("Country", on_delete=models.PROTECT)
    registered_at = models.DateTimeField(auto_now=True)


class Country(models.Model):
    name = models.CharField(max_length=24)
    code = models.CharField(
        max_length=4, blank=True, null=True, verbose_name=u'Codigo ISO', unique=True
    )

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"