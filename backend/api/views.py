from app.models import Download, Favorite, Follow, Ingredient, Recipe, Tag, IngredientForRecipe
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from collections import Counter
from functools import reduce

from .permissions import AnonymAdminAuthor
from .serializers import (DownloadSerializer, FavoriteSerializer,
                          FollowListSerializer, FollowSerializer,
                          IngredientsSerializer, ListRecipeSerializer,
                          RecipeSerializer, TagSerializer, UserSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [AnonymAdminAuthor]
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    ordering_fields = ('pub_date')
    #TODO:Решить как написать поля для фильтрации самой
    #filterset_fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListRecipeSerializer
        else:
            return RecipeSerializer
            
#@api_view(['POST'])
#def create_post(request):
    #serializer = RecipeSerializer(data=request.data,
    #                              context={'request': request})
    #if serializer.is_valid():
        #serializer.save()
        #return Response(serializer.data, status=status.HTTP_201_CREATED)
    #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(UserViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FollowAPI(APIView):

    def get(self, request, user_id):
        user = self.request.user
        author = get_object_or_404(User, id=user_id)
        follow = Follow.objects.filter(user=user, author=author)
        serializer = FollowSerializer(follow, many=True,
                                      data=request.data,
                                      context={'request': request})
        return Response(serializer.data)

    def post(self, request, user_id):
        data = {'user': request.user.id, 'author': user_id}
        serializer = FollowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        if not Follow.objects.filter(user=user, author=author).exists():
            return Response('Нельзя удалить подписку, которой нет!')
        Follow.objects.filter(user=user, author=author).delete()
        return Response('Подписка успешно удалена!',
                        status=status.HTTP_204_NO_CONTENT)


class FollowList(generics.ListAPIView):
    serializer_class = FollowListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(
            following__user=user
        )


class FavoriteAPI(APIView):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = Favorite.objects.filter(recipe=recipe, user=user)
        if favorite.exists():
            return Response(
                'Этот рецепт уже в избранном',
                status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(favorite, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = Favorite.objects.filter(recipe=recipe, user=user)
        if not favorite.exists():
            return Response(
                'Этот рецепт отсутствует в избранном',
                status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response('Рецепт успешно удален из избранного',
                        status=status.HTTP_204_NO_CONTENT)


class DownloadAPI(APIView):
    serializer_class = DownloadSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        download = Download.objects.filter(recipe=recipe, user=user)
        serializer = DownloadSerializer(download, many=True)
        return Response(serializer.data)

    def post(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        download = Download.objects.filter(recipe=recipe, user=user)
        if download .exists():
            return Response(
                'Этот рецепт уже в корзине',
                status=status.HTTP_400_BAD_REQUEST)
        Download.objects.create(user=user, recipe=recipe)
        serializer = DownloadSerializer(download, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        download = Download.objects.filter(recipe=recipe, user=user)
        if not download .exists():
            return Response(
                'Этот рецепт отсутствует в корзине',
                status=status.HTTP_400_BAD_REQUEST)
        Download.objects.filter(user=user, recipe=recipe).delete()
        return Response('Рецепт успешно удален из ссписка покупок',
                        status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    search_fields = ('^name',)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


@api_view(['GET'])
def download_list(request):
    user = request.user
    download = {}
    dls = Download.objects.filter(user=user).all()
    for dl in dls:
        racepe = dl.recipe
        ings = IngredientForRecipe.objects.filter(recipe=racepe)
        for ing in ings:
            amount = ing.amount
            unit = ing.ingredient.measurement_unit
            name = ing.ingredient.name
            if name not in download:
                download[name] = {'amount': amount, 'unit': unit}
            else:
                amount += download[name]['amount']
                download[name] = {'amount': amount, 'unit': unit}
        my_product_list = list()
        my_product_list.append(download)

    response = HttpResponse(my_product_list, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; my_product_list.txt'
    return response










