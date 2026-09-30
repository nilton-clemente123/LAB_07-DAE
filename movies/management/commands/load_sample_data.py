from django.core.management.base import BaseCommand

from movies.models import Genre, Movie, Person, Rating


class Command(BaseCommand):
    help = 'Carga datos de prueba: 4 géneros, 10 películas y valoraciones en al menos 5.'

    def handle(self, *args, **options):
        # 1) Géneros
        genres = {}
        for name in ('Acción', 'Drama', 'Comedia', 'Ciencia ficción'):
            genre, _ = Genre.objects.get_or_create(name=name)
            genres[name] = genre

        # 2) Personas (dirección y reparto)
        people = {}
        for name in (
            'Christopher Nolan', 'Quentin Tarantino', 'Bong Joon-ho',
            'Denis Villeneuve', 'Greta Gerwig', 'Damien Chazelle',
            'Alejandro González Iñárritu', 'Leonardo DiCaprio', 'Cillian Murphy',
            'Margot Robbie', 'Ryan Gosling', 'Emma Stone', 'Timothée Chalamet',
            'Ana de Armas',
        ):
            person, _ = Person.objects.get_or_create(name=name)
            people[name] = person

        # 3) Películas: título, año, géneros, dirección, reparto
        movies_data = [
            ('Origen', 2010, ['Acción', 'Ciencia ficción'], 'Christopher Nolan', ['Leonardo DiCaprio', 'Cillian Murphy']),
            ('Interstellar', 2014, ['Ciencia ficción', 'Drama'], 'Christopher Nolan', ['Cillian Murphy']),
            ('Dune', 2021, ['Ciencia ficción', 'Acción'], 'Denis Villeneuve', ['Timothée Chalamet']),
            ('Pulp Fiction', 1994, ['Drama', 'Acción'], 'Quentin Tarantino', ['Leonardo DiCaprio']),
            ('Parásitos', 2019, ['Drama', 'Comedia'], 'Bong Joon-ho', []),
            ('Barbie', 2023, ['Comedia'], 'Greta Gerwig', ['Margot Robbie', 'Ryan Gosling']),
            ('La La Land', 2016, ['Comedia', 'Drama'], 'Damien Chazelle', ['Emma Stone', 'Ryan Gosling']),
            ('El Renacido', 2015, ['Drama', 'Acción'], 'Alejandro González Iñárritu', ['Leonardo DiCaprio']),
            ('Érase una vez en Hollywood', 2019, ['Comedia', 'Drama'], 'Quentin Tarantino', ['Margot Robbie', 'Leonardo DiCaprio']),
            ('Blade Runner 2049', 2017, ['Ciencia ficción', 'Acción'], 'Denis Villeneuve', ['Ryan Gosling', 'Ana de Armas']),
        ]

        movies = {}
        for title, year, genre_names, director_name, cast_names in movies_data:
            movie, _ = Movie.objects.get_or_create(
                title=title, year=year, director=people[director_name],
            )
            movie.genres.set(genres[g] for g in genre_names)
            movie.cast.set(people[n] for n in cast_names)
            movies[title] = movie

        # 4) Valoraciones en 6 películas (>= 5)
        ratings_data = [
            ('Origen', 5, 'Obra maestra'),
            ('Origen', 4, 'Muy buena'),
            ('Interstellar', 5, 'Impresionante'),
            ('Dune', 4, ''),
            ('Dune', 5, 'Espectacular'),
            ('Parásitos', 5, 'Genial'),
            ('Parásitos', 5, ''),
            ('La La Land', 4, 'Muy bonita'),
            ('La La Land', 5, ''),
            ('Barbie', 4, 'Divertida'),
        ]
        for title, value, comment in ratings_data:
            Rating.objects.create(movie=movies[title], value=value, comment=comment)

        self.stdout.write(self.style.SUCCESS(
            'Datos de prueba cargados: 4 géneros, 10 películas y valoraciones en 6 de ellas.'
        ))
