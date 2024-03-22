from rest_framework import serializers
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    SlugRelatedField,
)

from reviews.models import Category, Comment, Genre, Review, Title


class GenreSerializer(ModelSerializer):
    """Сериализатор жанров."""

    class Meta:

        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(ModelSerializer):
    """Сериализатор категорий."""

    class Meta:

        model = Category
        fields = ('name', 'slug')


class TitleListSerializer(ModelSerializer):
    """Сериализатор произведений на выдачу."""

    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    rating = IntegerField(
        read_only=True, default=0
    )
    category = CategorySerializer(read_only=True,)

    class Meta:

        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category',
        )


class TitleSerializer(ModelSerializer):
    """Сериализатор произведений."""

    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field="slug"
    )
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug"
    )

    class Meta:

        fields = '__all__'
        model = Title

    def to_representation(self, instance):
        return TitleListSerializer(instance).data


class ReviewSerializer(ModelSerializer):
    """Сериализатор  отзывов."""

    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:

        fields = (
            'id', 'text', 'author', 'score', 'pub_date',
        )
        model = Review

    def validate(self, data):
        if self.context['request'].method == 'POST' and Review.objects.filter(
            author=self.context['request'].user,
            title_id=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise serializers.ValidationError(
                'Нельзя оставить два отзыва на одно произведение.'
            )
        return data


class CommentSerializer(ModelSerializer):
    """Сериализатор комментариев."""

    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:

        fields = (
            'id', 'text', 'author', 'pub_date',
        )
        model = Comment
