from django.views.generic import ListView
from .models import Article


class ArticleListView(ListView):
    model = Article
    template_name = 'article_list.html'
    context_object_name = 'articles'
    ordering = ['-pub_date']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('author', 'category')
        queryset = queryset.prefetch_related('tags')
        queryset = queryset.defer('content')
        return queryset
