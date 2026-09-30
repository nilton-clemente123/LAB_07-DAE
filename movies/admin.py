from django.contrib import admin

from .models import Genre, Movie, Person, Rating


class RatingInline(admin.TabularInline):
    """Permite dar de alta valoraciones desde el propio formulario de película."""
    model = Rating
    extra = 1
    fields = ('value', 'comment')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'director', 'genres_list', 'average_rating')
    list_filter = ('genres', 'year')
    search_fields = ('title', 'director__name', 'cast__name')
    inlines = (RatingInline,)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('genres', 'cast')
    fieldsets = (
        ('Datos principales', {
            'fields': ('title', 'year', 'poster', 'genres', 'director', 'cast'),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description='géneros')
    def genres_list(self, obj):
        return ', '.join(g.name for g in obj.genres.all())


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'movie_count')
    search_fields = ('name',)

    @admin.display(description='películas')
    def movie_count(self, obj):
        return obj.movies.count()


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'directed_count', 'acted_count')
    search_fields = ('name',)

    @admin.display(description='dirige')
    def directed_count(self, obj):
        return obj.directed_movies.count()

    @admin.display(description='actúa en')
    def acted_count(self, obj):
        return obj.acted_movies.count()


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'value', 'created_at')
    list_filter = ('value',)
    search_fields = ('movie__title',)
    readonly_fields = ('created_at',)
