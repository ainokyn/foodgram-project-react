from app.models import Recipe, Tag
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

User = get_user_model()


class FilterForRecipeFilter(filters.FilterSet):
    fovorite = filters.BooleanFilter(
        method='get_is_favorited')
    download = filters.BooleanFilter(
        method='get_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug', to_field_name='slug',
    )

    class Meta:
        fields = (
            'fovorite',
            'download',
            'tags'
        )

    def get_is_favorited(self, queryset, name, value):
        if value:
            Recipe.objects.filter(fovorite__user=self.request.user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(download__user=self.request.user)
        return Recipe.objects.all()
