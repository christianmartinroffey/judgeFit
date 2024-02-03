# Generated by Django 4.2.1 on 2024-02-03 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('athlete', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='affiliate',
            name='region',
        ),
        migrations.RemoveField(
            model_name='athlete',
            name='region',
        ),
        migrations.AddField(
            model_name='affiliate',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='affiliate',
            name='city',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='affiliate',
            name='crossfit_affiliate',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='affiliate',
            name='crossfit_affiliate_since',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='affiliate',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='static/images/affiliate_images'),
        ),
        migrations.AddField(
            model_name='affiliate',
            name='postal_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='affiliate',
            name='state',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='affiliate',
            name='website',
            field=models.URLField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Region',
        ),
    ]