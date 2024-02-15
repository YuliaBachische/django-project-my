from django.urls import path
from .views import ArticleListView, ArticlesDetailView, LatestArticlesFeed

appname = 'blogapp'

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='articles'),
    path('articles/<int:pk>/', ArticlesDetailView.as_view(), name='article'),
    path('articles/latest/feed/', LatestArticlesFeed(), name='articles-feed'),
]