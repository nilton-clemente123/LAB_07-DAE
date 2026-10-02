from django.shortcuts import get_object_or_404, render

from .models import Article, Category


def home(request):
    """Portada del portal: todas las noticias, de más reciente a más antigua."""
    articles = Article.objects.select_related('author').prefetch_related('categories')
    return render(request, 'news/home.html', {
        'articles': articles,
        'categories': Category.objects.all(),
    })


def article_detail(request, slug):
    """Detalle de una noticia: imagen, autor y categorías."""
    article = get_object_or_404(
        Article.objects.select_related('author').prefetch_related('categories'),
        slug=slug,
    )
    latest = Article.objects.exclude(pk=article.pk)[:5]
    return render(request, 'news/article_detail.html', {
        'article': article,
        'latest': latest,
        'categories': Category.objects.all(),
    })


def category_list(request, slug):
    """Listado de las noticias de una categoría (reutiliza la tarjeta)."""
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.select_related('author').prefetch_related('categories')
    return render(request, 'news/category_list.html', {
        'category': category,
        'articles': articles,
        'categories': Category.objects.all(),
    })

