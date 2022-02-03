from app.models import Download, Favorite, Follow
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


def get_subscribed(self, obj):
    """Method to get subscribers."""
    user = self.context.get('request').user
    if user.is_anonymous:
        return False
    return Follow.objects.filter(author=obj, user=user).exists()


def get_favorited(self, obj):
    """ Get favorite recipe."""
    curent_user = self.context.get('request').user
    return Favorite.objects.filter(recipe=obj, user=curent_user).exists()


def get_shopping_cart(self, obj):
    """ Get get recipe in shopping cart."""
    curent_user = self.context.get('request').user
    return Download.objects.filter(recipe=obj, user=curent_user).exists()


def val_cooking_time(self, cooking_time):
    """ Check the time of cooking."""
    if cooking_time <= 1:
        raise serializers.ValidationError("Время приготовления должно"
                                          "быть от 1 минуты")
    return cooking_time
