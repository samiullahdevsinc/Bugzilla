# Generated by Django 4.1.4 on 2023-08-28 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('management', '0021_alter_bug_screenshot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='developer',
            field=models.ManyToManyField(blank=True, related_name='projects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='managers',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='managed_projects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='qa',
            field=models.ManyToManyField(blank=True, related_name='projectsq', to=settings.AUTH_USER_MODEL),
        ),
    ]
