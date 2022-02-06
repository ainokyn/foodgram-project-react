from app.models import Recipe, Tag
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

User = get_user_model()


class FilterForRecipeFilter(filters.FilterSet):
    tags = filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    download = filters.BooleanFilter(
        field_name='download', method='filter'
    )
    fovorite = filters.BooleanFilter(
        field_name='fovorite', method='filter'
    )

    def filter(self, queryset, name, value):
        if name == 'download' and value:
            queryset = queryset.filter(
                download__user=self.request.user
            )
        if name == 'fovorite' and value:
            queryset = queryset.filter(
                fovorite__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'download', 'fovorite']
