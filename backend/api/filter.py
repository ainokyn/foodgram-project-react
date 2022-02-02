from django.contrib.auth import get_user_model
User = get_user_model()
from django_filters import rest_framework as filters
from app.models import Download, Favorite, Recipe, Tag
from django_filters.fields import CSVWidget

class FilterForRecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter('get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter('get_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(), widget=CSVWidget,
        method='filter_tags'
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'tags']

    def get_is_favorited(self, request):
        user = self.request
        return Favorite.objects.filter(fovorite__user=user)

    def get_is_in_shopping_cart(self, request):
        user = self.request
        return Download.objects.filter(download__user=user)

    def filter_tags(self, queryset, value):
        if value:
            queryset = queryset.filter(tags__slug=value)
        return queryset
