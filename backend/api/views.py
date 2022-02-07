from app.models import (Download, Favorite, Follow, Ingredient,
                        IngredientForRecipe, Recipe, Tag)
from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter import FilterForIngredients, FilterForRecipeFilter
from .permissions import AnonymAdminAuthor
from .serializers import (DownloadSerializer, FavoriteSerializer,
                          FollowListSerializer, FollowSerializer,
                          IngredientsSerializer, ListRecipeSerializer,
                          PasswordSerializer, RecipeSerializer, TagSerializer,
                          UserSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Tag endpoint handler."""
    permission_classes = [AllowAny]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ingredient endpoint handler."""
    permission_classes = [AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterForIngredients


class FollowAPI(APIView):
    """Follow change/create endpoint handler."""
    permission_classes = (permissions.IsAuthenticated,)

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
    """Follow list endpoint handler."""
    serializer_class = FollowListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(
            following__user=user
        )


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipe/favorite/shopping_cart/download endpoint handler."""
    permission_classes = [AnonymAdminAuthor]
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    ordering_fields = ('pub_date')
    filterset_class = FilterForRecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListRecipeSerializer
        else:
            return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        download = Download.objects.filter(recipe=recipe, user=user)
        if self.request.method == 'POST':
            if download.exists():
                return Response('Этот рецепт уже в корзине',
                                status=status.HTTP_400_BAD_REQUEST)
            Download.objects.create(user=user, recipe=recipe)
            serializer = DownloadSerializer(download, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if not download.exists():
                return Response('Этот рецепт отсутствует в корзине',
                                status=status.HTTP_400_BAD_REQUEST)
            Download.objects.filter(user=user, recipe=recipe).delete()
            return Response('Рецепт успешно удален из ссписка покупок',
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            url_path='download_shopping_cart',
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
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
        for key in download:
            my_product_list.append(f'{key} : {download[key]["amount"]} '
                                   f'{download[key]["unit"]} \n')
        response = HttpResponse(my_product_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; my_product_list.txt'
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(recipe=recipe, user=user)
        if self.request.method == 'POST':
            if favorite.exists():
                return Response('Этот рецепт уже в избранном',
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if not favorite.exists():
                return Response('Этот рецепт отсутствует в избранном',
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response('Рецепт успешно удален из избранного',
                            status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    """User endpoint handler."""
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        self.kwargs['pk'] = request.user.pk
        if request.method == 'GET':
            return self.retrieve(request)
        else:
            raise Exception('другой метод не доступен')

    @action(['post'], detail=False, url_path='set_password')
    def set_password(self, request):
        user = self.request.user
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
