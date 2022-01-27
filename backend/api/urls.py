from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from . import views
from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,  FollowList, FollowAPI, FavoriteAPI, DownloadAPI)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet, basename='ingredient')
urlpatterns = [
     path('', include(router.urls)),
     path('users/subscriptions/', FollowList.as_view(),
          name='follow_list'),
     path('users/<int:user_id>/subscribe/', FollowAPI.as_view(),
          name='follow'),
     path('recipes/<int:favorite_id>/favorite/', FavoriteAPI.as_view(),
          name='favorite'),
     path('recipes/<int:recipe_id>/shopping_cart/', DownloadAPI.as_view(),
          name='shopping_cart'),
     path('recipes/download_shopping_cart/', views.download_list, name='list'),

]
