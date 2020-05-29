# Generated by Django 3.0.3 on 2020-05-18 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hill', '0002_hillprogram_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hillgame',
            name='left',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Left', to='hill.HillProgram'),
        ),
        migrations.AlterField(
            model_name='hillgame',
            name='right',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Right', to='hill.HillProgram'),
        ),
    ]