# Generated by Django 4.2.1 on 2024-02-03 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('athlete', '0003_country_router_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliate',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]