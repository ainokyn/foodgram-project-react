# Generated by Django 2.2.16 on 2022-01-22 19:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20220122_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientforrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='app.Recipe', verbose_name='ingredient_recipe'),
        ),
    ]
