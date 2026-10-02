from django.contrib import admin

from .models import Article, Author, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'article_count')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='noticias')
    def article_count(self, obj):
        return obj.articles.count()


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_count')
    list_filter = ('name',)
    search_fields = ('name', 'bio')

    @admin.display(description='noticias')
    def article_count(self, obj):
        return obj.articles.count()


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'author', 'categories_list')
    list_filter = ('categories', 'published_at', 'author')
    search_fields = ('title', 'body', 'author__name')
    date_hierarchy = 'published_at'
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories',)
    fieldsets = (
        ('Noticia', {
            'fields': ('title', 'slug', 'author', 'categories', 'image', 'body'),
        }),
        ('Publicación', {
            'fields': ('published_at',),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='categorías')
    def categories_list(self, obj):
        return ', '.join(c.name for c in obj.categories.all())

