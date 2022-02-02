from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

TAG_CHOICES = (
    ('Завтрак', 'Завтрак'),
    ('Обед', 'Обед'),
    ('Ужин', 'Ужин'),
)


class Ingredient(models.Model):
    """The model describes the ingredients of the dish."""
    name = models.CharField(max_length=300, verbose_name='ingredient_name',
                            null=False, blank=False,)
    measurement_unit = models.CharField(max_length=50,
                                        verbose_name='ingredient_unit',
                                        null=False, blank=False,)

    class Meta:
        """Performs sorting."""
        ordering = ('id',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """The model describes the tag."""
    name = models.CharField(
        max_length=30,
        choices=TAG_CHOICES,
        default='Завтрак',
        verbose_name='name_of_tag'
    )
    code = models.CharField(max_length=30, verbose_name='tag_color',
                            null=False, blank=False, unique=True,)
    slug = models.SlugField(max_length=50, verbose_name='tag_slug',
                            unique=True, null=False, blank=False)

    class Meta:
        """Performs sorting."""
        ordering = ('id',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """The model describes the recipe of the dish."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='author_recipe',
        related_name='recipes'
    )
    name = models.CharField(max_length=300, verbose_name='recipe_name',
                            null=False, blank=False)
    image = models.ImageField(upload_to='media/', null=False, blank=False,
                              verbose_name='recipe_photo')
    text = models.TextField(null=False, blank=False,
                            verbose_name='recipe_text')
    ingredient = models.ManyToManyField(Ingredient, blank=False,
                                        through='IngredientForRecipe',
                                        related_name='ingredients')
    tags = models.ManyToManyField(Tag, blank=False, related_name='tags',
                                  verbose_name='recipe_tag')
    cooking_time = models.FloatField(null=False, blank=False,
                                     verbose_name='recipe_time', default=1)
    pub_date = models.DateTimeField(verbose_name='date of publication recipe',
                                    auto_now_add=True, db_index=True)

    class Meta:
        """Performs sorting."""
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientForRecipe(models.Model):
    """The model describes the ingredients for recipe."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe',
        verbose_name='name_ingredient_for_recipe',
    )
    amount = models.FloatField(max_length=50,
                               verbose_name='ingredient_for_recipe_amount')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='ingredient_recipe',
        related_name='ingredients_recipe',
        blank=False
    )

    class Meta:
        """Performs sorting."""
        ordering = ('id',)
        verbose_name = 'Ingredient_for_recipe'
        verbose_name_plural = 'Ingredients_for_recipe'

    def __str__(self):
        return f'{self.recipe} {self.amount}'


class Follow(models.Model):
    """The model describes the follow."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        """Performs sorting."""
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]


class Favorite(models.Model):
    """The model describes the favorite."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='user_who_has_favorite_recipe',
        related_name='fovorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='favorite_recipe',
        related_name='fovorite'
    )

    class Meta:
        """Performs sorting."""
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite_recipe')
            ]


class Download(models.Model):
    """The model describes the downloads_cart."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='user_who_has_download_recipe',
        related_name='download'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='download_recipe',
        related_name='download'
    )

    class Meta:
        """Performs sorting."""
        verbose_name = 'Download'
        verbose_name_plural = 'Downloads'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_download_recipe')
            ]
