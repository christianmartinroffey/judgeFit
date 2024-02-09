# Generated by Django 4.2.1 on 2024-02-09 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('athlete', '0006_competition'),
        ('workout', '0006_alter_movement_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('description', models.TextField(blank=True, max_length=1500, null=True)),
                ('type', models.CharField(choices=[('AMRAP', 'As Many Reps As Possible'), ('FT', 'For Time'), ('FW', 'For Weight')], max_length=5)),
                ('total_reps', models.IntegerField(blank=True, null=True)),
                ('time_cap', models.IntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_scaled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(default=0)),
                ('reps', models.CharField(blank=True, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('movement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.movement')),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='workout.workout')),
            ],
            options={
                'ordering': ['sequence'],
            },
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_valid', models.BooleanField(default=True)),
                ('total_reps', models.IntegerField(blank=True, null=True)),
                ('no_reps', models.IntegerField(blank=True, null=True)),
                ('score', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='athlete.athlete')),
                ('competition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='athlete.competition')),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.workout')),
            ],
        ),
    ]