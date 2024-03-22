"""
Проект состоит из следующих страниц:

главная,
страница рецепта,
страница пользователя,
страница подписок,
избранное,
список покупок,
создание и редактирование рецепта.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from api.views import *
from users import views

app_name = 'api'


router_v1 = DefaultRouter()
router_v1.register('users', views.UsersViewSet, basename='users')
# router_v1.register('titles', TitleViewSet, basename='titles')
# router_v1.register('genres', GenreViewSet, basename='genres')
# router_v1.register("categories", CategoryViewSet, basename="categories")
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='reviews',
# )
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments',
# )

v1_urls = [
    path('', include(router_v1.urls)),
    # path('auth/', include([
    #     path('signup/', views.SignUpView.as_view()),
    #     path('token/', views.TokenView.as_view()),
    # ])),
]

urlpatterns = [
    path('v1/', include(v1_urls)),
]
