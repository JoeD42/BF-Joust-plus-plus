# Generated by Django 3.0.3 on 2020-05-18 16:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HillProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('rank', models.IntegerField()),
                ('prev_rank', models.IntegerField()),
                ('points', models.IntegerField()),
                ('score', models.IntegerField()),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HillGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField()),
                ('games', models.TextField()),
                ('left', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Right', to='hill.HillProgram')),
                ('right', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Left', to='hill.HillProgram')),
            ],
        ),
    ]