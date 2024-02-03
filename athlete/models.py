from django.db import models


class Athlete(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other')
    ]
    name = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=2)
    date_of_birth = models.DateField()
    height = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    email = models.EmailField(max_length=100)
    country = models.ForeignKey("Country", on_delete=models.PROTECT)
    region = models.ForeignKey('Region', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=True)
    affiliate = models.ForeignKey("Affiliate", on_delete=models.PROTECT)
    profile_photo = models.ImageField(upload_to='static/images/')
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Athlete"
        verbose_name_plural = "Athletes"


class Affiliate(models.Model):
    name = models.CharField(max_length=40)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=40)
    postal_code = models.CharField(max_length=10)
    website = models.URLField(max_length=100)
    country = models.ForeignKey("Country", on_delete=models.PROTECT)
    state = models.CharField(max_length=40)
    crossfit_affiliate = models.BooleanField(default=False)
    crossfit_affiliate_since = models.DateField()
    created_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='static/images/affiliate_images')

    class Meta:
        verbose_name = "Affiliate"
        verbose_name_plural = "Affiliates"


class Country(models.Model):
    name = models.CharField(max_length=24)
    code = models.CharField(
        max_length=4, blank=True, null=True, verbose_name=u'ISO Code', unique=True
    )

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
