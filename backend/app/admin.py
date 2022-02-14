from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (Download, Favorite, Follow, Ingredient,
                     IngredientForRecipe, Recipe, Tag)

User = get_user_model()


class IngredientForRecipeSubjectInline(admin.TabularInline):
    model = IngredientForRecipe
    extra = 6


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Class that configures the display of Recipe model. """
    list_display = ('id', 'author', 'name', "show_favorite")
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('author__username', '^name', 'tags__name',)
    empty_value_display = '-пусто-'
    inlines = (IngredientForRecipeSubjectInline,)

    def show_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Class that configures the display of Ingredient model. """
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('^name',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Class that configures the display of Follow model. """
    list_display = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__username', 'id', )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Class that configures the display of Tag model. """
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('^name',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Class that configures the display of Favorite model. """
    list_display = ('id', 'user', 'recipe')
    search_fields = ('id', 'user__username', 'recipe__name',)
    empty_value_display = '-пусто-'


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    """Class that configures the display of Download model. """
    list_display = ('id', 'user', 'recipe')
    search_fields = ('id', 'user__username', 'recipe__name',)
    empty_value_display = '-пусто-'
