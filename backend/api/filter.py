from app.models import Recipe, Tag
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

User = get_user_model()


class FilterForRecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug', to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'tags'
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(download__user=self.request.user)
        return Recipe.objects.all()

    def filter(self, queryset, name, value):
        if name == 'is_favorited' and value:
            queryset = queryset.filter(
                fovorite__user__user=self.request.user
            )
        return queryset
