from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (IngredientViewSet, TagViewSet,  FollowList, FollowAPI,
                    RecipeViewSet, UserViewSet)

router = DefaultRouter()
router.register("users", UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tag')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
     path('users/subscriptions/', FollowList.as_view(),
          name='follow_list'),
     path('users/<int:user_id>/subscribe/', FollowAPI.as_view(),
          name='follow'),
     path('', include(router.urls)),

]
