from django.db.models import Avg
from django.shortcuts import get_object_or_404, render

from .models import Movie


def movie_list(request):
    """Página pública con la cartelera (lista de películas)."""
    movies = Movie.objects.all().order_by('title')
    return render(request, 'movies/movie_list.html', {'movies': movies})


def recommendations(request, movie_id):
    """Películas del mismo género que la indicada, ordenadas por mejor valoración."""
    movie = get_object_or_404(Movie, pk=movie_id)
    genres = movie.genres.all()
    recommended = (
        Movie.objects
        .filter(genres__in=genres)
        .exclude(pk=movie.pk)
        .annotate(avg_rating=Avg('ratings__value'))
        .order_by('-avg_rating', 'title')
        .distinct()
    )
    return render(request, 'movies/recommendations.html', {
        'movie': movie,
        'recommended': recommended,
    })
