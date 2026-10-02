from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """Categoría temática del portal (Tecnología, Deportes, Cultura...)."""
    name = models.CharField('nombre', max_length=100, unique=True)
    slug = models.SlugField('slug', max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:category_list', args=[self.slug])


class Author(models.Model):
    """Autor o autora de las noticias del portal."""
    name = models.CharField('nombre', max_length=150)
    bio = models.TextField('biografía', blank=True)
    avatar = models.ImageField('avatar', upload_to='authors/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'autor'
        verbose_name_plural = 'autores'

    def __str__(self):
        return self.name


class Article(models.Model):
    """Noticia del portal: imagen destacada, fecha de publicación y relaciones."""
    title = models.CharField('título', max_length=200)
    slug = models.SlugField('slug', max_length=220, unique=True)
    body = models.TextField('cuerpo')
    image = models.ImageField('imagen destacada', upload_to='articles/', blank=True)
    published_at = models.DateTimeField('fecha de publicación', default=timezone.now)
    author = models.ForeignKey(
        Author, verbose_name='autor', related_name='articles',
        on_delete=models.PROTECT,
    )
    categories = models.ManyToManyField(
        Category, verbose_name='categorías', related_name='articles', blank=True,
    )
    # Campos de auditoría (mismo patrón que la app movies)
    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('modificado el', auto_now=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'noticia'
        verbose_name_plural = 'noticias'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:article_detail', args=[self.slug])

