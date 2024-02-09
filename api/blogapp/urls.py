from django.urls import path
from .views import ArticleListView

appname = 'blogapp'

urlpatterns = [
    path('articles-list/', ArticleListView.as_view(), name='articles-list'),
]