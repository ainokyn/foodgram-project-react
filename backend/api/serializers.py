import base64
import imghdr
import uuid

from app.models import (Download, Favorite, Follow, Ingredient,
                        IngredientForRecipe, Recipe, Tag)
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .function import (get_favorited, get_shopping_cart, get_subscribed,
                       val_cooking_time)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Serializer for image field."""

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


class UserSerializer(UserCreateSerializer):
    """Serializer for user requests."""
    is_subscribed = serializers.SerializerMethodField()
    first_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password')

    def get_is_subscribed(self, obj):
        return get_subscribed(self, obj)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag requests."""

    class Meta:
        model = Tag
        fields = '__all__'
        lookup_field = 'slug'


class IngredientsSerializer(serializers.ModelSerializer):
    """Serializer for ingredients requests."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsForCreateRecipeSerializer(serializers.ModelSerializer):
    """Serializer for ingredients for create recipe requests."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class IngredientsForRecipeSerializer(serializers.ModelSerializer):
    """Serializer for ingredients  for recipe requests."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.ReadOnlyField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ListRecipeSerializer(serializers.ModelSerializer):
    """Serializer for read recipe requests."""
    tags = TagSerializer(many=True,)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_cooking_time(self, cooking_time):
        return val_cooking_time(self, cooking_time)

    def get_ingredients(self, recipe):
        """ Get pull of ingreients for recipe."""
        queryset = IngredientForRecipe.objects.filter(
            recipe__id=recipe.id).all()
        return IngredientsForRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        return get_favorited(self, obj)

    def get_is_in_shopping_cart(self, obj):
        return get_shopping_cart(self, obj)


class RecipeFollowtSerializer(serializers.ModelSerializer):
    """ Auxiliary serializer for dispensing prescriptions."""
    image = serializers.SerializerMethodField(method_name='get_image')

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time')

    def get_image(self, recipe):
        request = self.context.get('request')
        image = recipe.image.url
        return request.build_absolute_uri(image)


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
        """Method to override response fields."""
        serializer = RecipeFollowtSerializer(
            instance.recipe,
            context={'request': self.context.get('request')})
        return serializer.data


class FollowListSerializer(serializers.ModelSerializer):
    """Serializer for list follows requests."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        return get_subscribed(self, obj)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if limit is not None:
            queryset = Recipe.objects.filter(
                author=obj
            )[:int(limit)]
        return RecipeFollowtSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Recipe counting method."""
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for write subscribrd requests."""

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(message='Такая подписка есть!',
                                    queryset=Follow.objects.all(),
                                    fields=('user', 'author'))]

    def to_representation(self, instance):
        """Method to override response fields."""
        serializer = FollowListSerializer(
            instance.author,
            context={'request': self.context.get('request')})
        return serializer.data

    def validate(self, data):
        """Self-subscription validation."""
        user = data['user']
        author = data['author']
        if user == author:
            raise serializers.ValidationError('Нельзя на себя подписываться!')
        return data


class DownloadSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart requests."""
    user = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all())
    recipe = serializers.SlugRelatedField(
        slug_field='name', queryset=Recipe.objects.all(),
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Download
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Download.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        """Method to override response fields."""
        serializer = RecipeFollowtSerializer(
            instance.recipe,
            context={'request': self.context.get('request')})
        return serializer.data


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for create recipe."""
    ingredients = IngredientsForCreateRecipeSerializer(
        many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'cooking_time', 'id', 'author',
                  'tags', 'ingredients', 'image')

    def validate_cooking_time(self, cooking_time):
        return val_cooking_time(self, cooking_time)

    def to_representation(self, instance):
        """Method to override response fields."""
        serializer = ListRecipeSerializer(
            instance,
            context={'request': self.context.get('request')})
        return serializer.data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients_data:
            ing = ingredient['ingredient']
            amount = ingredient['amount']
            if amount <= 0:
                raise serializers.ValidationError('Количество ингредиентов'
                                                  ' должно быть больше 0')
            ing_for_rec = IngredientForRecipe.objects.create(
                ingredient=ing,
                amount=amount,
                recipe=recipe)
        recipe.tags.set(tags)
        ing_for_rec.save()
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance.author = validated_data.get('author', instance.author)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.pub_date = validated_data.get('pub_date', instance.pub_date)
        instance.tags.set(tags)
        instance.save()
        ingredients_data = validated_data.pop('ingredients')
        IngredientForRecipe.objects.filter(recipe=instance).all().delete()
        for ingredient in ingredients_data:
            ing = ingredient['ingredient']
            amount = ingredient['amount']
            if amount <= 0:
                raise serializers.ValidationError('Количество ингредиентов'
                                                  ' должно быть больше 0')
            ing_for_rec = IngredientForRecipe.objects.create(
                ingredient=ing,
                amount=amount,
                recipe=instance)
            ing_for_rec.save()
        return instance


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError("passwords must not match")
        try:
            validate_password(data['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)})
        return super().validate(data)
