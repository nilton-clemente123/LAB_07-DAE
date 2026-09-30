from django.db import models


class Genre(models.Model):
    """Género cinematográfico (acción, drama, comedia, ciencia ficción...)."""
    name = models.CharField('nombre', max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'género'
        verbose_name_plural = 'géneros'

    def __str__(self):
        return self.name


class Person(models.Model):
    """Persona que interviene en películas (en la dirección o en el reparto)."""
    name = models.CharField('nombre', max_length=150)

    class Meta:
        ordering = ['name']
        verbose_name = 'persona'
        verbose_name_plural = 'personas'

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField('título', max_length=200)
    year = models.PositiveIntegerField('año')
    poster = models.ImageField('cartel', upload_to='posters/', blank=True, null=True)
    genres = models.ManyToManyField(
        Genre, verbose_name='géneros', related_name='movies',
    )
    director = models.ForeignKey(
        Person, verbose_name='dirección', related_name='directed_movies',
        on_delete=models.PROTECT,
    )
    cast = models.ManyToManyField(
        Person, verbose_name='reparto', related_name='acted_movies', blank=True,
    )
    # Campos de auditoría
    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('modificado el', auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'película'
        verbose_name_plural = 'películas'

    def __str__(self):
        return f'{self.title} ({self.year})'

    @property
    def average_rating(self):
        """Nota media de las valoraciones recibidas (None si no tiene)."""
        values = [r.value for r in self.ratings.all()]
        if not values:
            return None
        return round(sum(values) / len(values), 1)


class Rating(models.Model):
    class Stars(models.IntegerChoices):
        ONE = 1, '★'
        TWO = 2, '★★'
        THREE = 3, '★★★'
        FOUR = 4, '★★★★'
        FIVE = 5, '★★★★★'

    movie = models.ForeignKey(
        Movie, verbose_name='película', related_name='ratings',
        on_delete=models.CASCADE,
    )
    value = models.PositiveSmallIntegerField(
        'valoración', choices=Stars.choices, default=Stars.THREE,
    )
    comment = models.TextField('comentario', blank=True)
    created_at = models.DateTimeField('creado el', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'valoración'
        verbose_name_plural = 'valoraciones'

    def __str__(self):
        return f'{self.movie.title}: {self.value}'
