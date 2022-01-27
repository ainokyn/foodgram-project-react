import base64
import imghdr
import uuid

from app.models import (Download, Favorite, Follow, Ingredient,
                        IngredientForRecipe, Recipe, Tag)
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import request
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if 'data:' in data and ';base64,' in data:
            header, data = data.split(';base64,')
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            self.fail('invalid_image')
        file_name = str(uuid.uuid4())[:20]
        file_extension = self.get_file_extension(file_name, decoded_file)
        complete_file_name = "%s.%s" % (file_name, file_extension, )
        data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(author=obj, user=user).exists()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag requests."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    """Serializer for ingredients requests."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientsForCreateRecipeSerializer(serializers.Serializer):
    """Serializer for ingredients requests."""
    amount = serializers.IntegerField()
    id = serializers.IntegerField()


class IngredientsForRecipeSerializer(serializers.ModelSerializer):
    """Serializer for ingredients requests."""
    id = serializers.ReadOnlyField(source='ingredients.id', read_only=True)
    name = serializers.ReadOnlyField(source='ingredients.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit', read_only=True)
    amount = serializers.ReadOnlyField(read_only=True)

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, amount):
        """ Check the amount."""
        if amount <= 0.0:
            raise serializers.ValidationError("Количество ингредиента должно"
                                              "быть больше 0")
        return amount


class ListRecipeSerializer(serializers.ModelSerializer):
    """Serializer for read recipe requests."""
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    tags = TagSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart')
    ingredients = serializers.SerializerMethodField(method_name='get_ingredients')

    class Meta:
        model = Recipe
        fields = ("__all__")

    def validate_cooking_time(self, cooking_time):
        """ Check thr time of cooking."""
        if cooking_time <= 1:
            raise serializers.ValidationError("invalid value")
        return cooking_time

    def get_ingredients(self, recipe):
        queryset = IngredientForRecipe.objects.filter(recipe__id=recipe.id).all()
        return IngredientsForRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        curent_user = self.context.get('request').user
        return Favorite.objects.filter(recipe=obj, user=curent_user).exists()

    def get_is_in_shopping_cart(self, obj):
        curent_user = self.context.get('request').user
        return Download.objects.filter(recipe=obj, user=curent_user).exists()

class RecipeFollowtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time')

class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorite recipe requests."""
    recipe = serializers.SlugRelatedField(
        slug_field='name', queryset=Recipe.objects.all())
    user = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]
    
    def to_representation(self, instance):
        serializer = RecipeFollowtSerializer(instance.recipe, context={'request': self.context.get('request')})
        return serializer.data



class FollowListSerializer(serializers.ModelSerializer):
    """Serializer for subscribrd requests."""
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(author=obj, user=user).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        print(queryset)
        return RecipeFollowtSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ('email',  'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for subscribrd requests."""
    author = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all()
       )
    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    #is_subscribed = serializers.SerializerMethodField('get_is_subscribed')
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')

    def get_recipes(self,  obj):
        queryset = Recipe.objects.filter(author=obj.author)
        return RecipeFollowtSerializer(queryset, many=True).data

    def get_recipes_count(self,  obj):
        return Recipe.objects.filter(author=obj.author).count()

    #def get_is_subscribed(self, obj):
        #TODO:не работает оценка подписки
        #user = self.context.get("user")
        #if user.is_anonymous:
            #return False
        #return Follow.objects.filter(author=obj, user=user).exists()

    class Meta:
        model = Follow
        fields = '__all__'


class DownloadSerializer(serializers.ModelSerializer):
    """Serializer for subscribrd requests."""
    author = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all())
    user = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Download
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Download.objects.all(),
                fields=('user', 'author')
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for create recipe."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientsForCreateRecipeSerializer(many=True)
    cooking_time = serializers.FloatField()
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'cooking_time', 'id', 'author',
                  'tags', 'ingredients', 'image')

    def validate_cooking_time(self, cooking_time):
        """ Check thr time of cooking."""
        if cooking_time < 1:
            raise serializers.ValidationError("invalid value")
        return cooking_time

    def create(self, validated_data,):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author,  **validated_data)
        for ingredients in ingredients_data:
            ing = Ingredient.objects.get(id=ingredients['id'])
            ing_for_rep, created = IngredientForRecipe.objects.get_or_create(
                ingredients=ing,
                amount=ingredients['amount'],
                recipe=recipe,
            )
            print('after', ing_for_rep, created)
        recipe.tags.set(tags)
        recipe.save()
        print('before return: ', recipe)
        return recipe
