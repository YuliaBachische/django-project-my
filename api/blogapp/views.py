from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from .models import Article
from django.urls import reverse, reverse_lazy


class ArticleListView(ListView):
    # model = Article
    # template_name = 'article_list.html'
    # context_object_name = 'articles'
    # ordering = ['-pub_date']
    # paginate_by = 10
    #
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     queryset = queryset.select_related('author', 'category')
    #     queryset = queryset.prefetch_related('tags')
    #     queryset = queryset.defer('content')
    #     return queryset
    queryset = (
        Article.objects
        .filter(pub_date__isnull=False)
        .order_by('-pub_date')
    )


class ArticlesDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Latest articles"
    description = "Updates on changes and additions to articles"
    link = reverse_lazy('articles')

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by('-pub_date')[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]


