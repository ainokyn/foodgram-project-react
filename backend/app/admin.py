from django.contrib import admin

from .models import Ingredient, IngredientForRecipe, Recipe, Tag, Follow
admin.site.register(Tag)
admin.site.register(Follow)

class IngredientForRecipeSubjectInline(admin.TabularInline):
    model = IngredientForRecipe
    extra = 6

class RecipeAdmin(admin.ModelAdmin):
    """Class that configures the display of Recipe model. """
    list_display = ('author', 'name',)
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'
    inlines = (IngredientForRecipeSubjectInline,)


class IngredientAdmin(admin.ModelAdmin):
    """Class that configures the display of Ingredient model. """
    list_display = ('name', 'measurement_unit', 'pk')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'



admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
