from django_filters.rest_framework import FilterSet, filters

from food.models import Ingredient, Recipe, Tag, Subscription, Favourites
from django.contrib.auth import get_user_model
User = get_user_model()


