# Generated by Django 2.2.16 on 2022-02-01 15:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20220129_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fovorite', to='app.Recipe', verbose_name='favorite_recipe'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fovorite', to=settings.AUTH_USER_MODEL, verbose_name='user_who_has_favorite_recipe'),
        ),
    ]
