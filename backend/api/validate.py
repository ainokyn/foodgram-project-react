from app.models import (Download, Favorite, Follow, Ingredient,
                        IngredientForRecipe, Recipe, Tag)

def get_is_subscribed(self, obj):
        curent_user = self.context.get('request').user
        if curent_user.is_anonymous:
            return False
        return Follow.objects.filter(author=obj, user=curent_user).exists()
