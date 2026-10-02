from django.contrib import admin
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from .admin import RatingInline
from .models import Genre, Movie, Person, Rating


class ModelTestCase(TestCase):
    """Comprueba la representación y la nota media de los modelos."""

    def setUp(self):
        self.accion = Genre.objects.create(name='Acción')
        self.drama = Genre.objects.create(name='Drama')
        self.nolan = Person.objects.create(name='Christopher Nolan')
        self.dicaprio = Person.objects.create(name='Leonardo DiCaprio')
        self.movie = Movie.objects.create(
            title='Origen', year=2010, director=self.nolan,
        )
        self.movie.genres.add(self.accion, self.drama)
        self.movie.cast.add(self.dicaprio)

    def test_str_de_los_modelos(self):
        self.assertEqual(str(self.movie), 'Origen (2010)')
        self.assertEqual(str(self.accion), 'Acción')
        self.assertEqual(str(self.nolan), 'Christopher Nolan')

    def test_average_rating_sin_valoraciones_es_none(self):
        self.assertIsNone(self.movie.average_rating)

    def test_average_rating_calcula_la_media(self):
        Rating.objects.create(movie=self.movie, value=5)
        Rating.objects.create(movie=self.movie, value=3)
        self.assertEqual(self.movie.average_rating, 4.0)


class RecommendationViewTest(TestCase):
    """Comprueba la vista pública de recomendaciones por género."""

    def setUp(self):
        self.accion = Genre.objects.create(name='Acción')
        self.drama = Genre.objects.create(name='Drama')
        self.nolan = Person.objects.create(name='Christopher Nolan')
        self.villeneuve = Person.objects.create(name='Denis Villeneuve')

        self.origen = Movie.objects.create(title='Origen', year=2010, director=self.nolan)
        self.origen.genres.add(self.accion, self.drama)

        self.dune = Movie.objects.create(title='Dune', year=2021, director=self.villeneuve)
        self.dune.genres.add(self.accion)

        self.lalaland = Movie.objects.create(title='La La Land', year=2016, director=self.villeneuve)
        self.lalaland.genres.add(self.drama)

        Rating.objects.create(movie=self.origen, value=5)
        Rating.objects.create(movie=self.dune, value=3)
        Rating.objects.create(movie=self.lalaland, value=4)

    def test_movie_list_muestra_la_cartelera(self):
        response = self.client.get(reverse('movies:movie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['movies']), [self.dune, self.lalaland, self.origen])

    def test_recomendaciones_excluyen_la_propia_pelicula(self):
        response = self.client.get(reverse('movies:recommendations', args=[self.origen.id]))
        self.assertEqual(response.status_code, 200)
        recommended = list(response.context['recommended'])
        self.assertNotIn(self.origen, recommended)

    def test_recomendaciones_ordenadas_por_mejor_nota(self):
        response = self.client.get(reverse('movies:recommendations', args=[self.origen.id]))
        recommended = list(response.context['recommended'])
        # La La Land (4.0) antes que Dune (3.0), ambas del mismo género que Origen.
        self.assertEqual(recommended, [self.lalaland, self.dune])


class PermissionTestCase(TestCase):
    """Comprueba que el rol «editor» ve solo lo que le corresponde."""

    def setUp(self):
        self.group = Group.objects.create(name='editores')
        ct = ContentType.objects.get_for_model(Movie)
        for codename in ('add_movie', 'change_movie', 'view_movie'):
            self.group.permissions.add(
                Permission.objects.get(content_type=ct, codename=codename)
            )
        self.editor = User.objects.create_user(username='editor', password='x')
        self.editor.is_staff = True
        self.editor.groups.add(self.group)

    def test_editor_puede_aniadir_cambiar_y_ver_peliculas(self):
        self.assertTrue(self.editor.has_perm('movies.add_movie'))
        self.assertTrue(self.editor.has_perm('movies.change_movie'))
        self.assertTrue(self.editor.has_perm('movies.view_movie'))

    def test_editor_no_puede_borrar_peliculas(self):
        self.assertFalse(self.editor.has_perm('movies.delete_movie'))

    def test_editor_no_gestiona_otros_modelos(self):
        self.assertFalse(self.editor.has_perm('movies.add_genre'))
        self.assertFalse(self.editor.has_perm('movies.add_rating'))
        self.assertFalse(self.editor.has_perm('movies.change_person'))


class AdminRegistrationTest(TestCase):
    """Comprueba el registro y la personalización del panel."""

    def test_los_cuatro_modelos_estan_registrados(self):
        for model in (Genre, Movie, Person, Rating):
            self.assertTrue(admin.site.is_registered(model))

    def test_movie_admin_personalizado(self):
        model_admin = admin.site._registry[Movie]
        self.assertEqual(model_admin.list_display[0], 'title')
        self.assertIn('genres', model_admin.list_filter)
        self.assertIn('year', model_admin.list_filter)
        self.assertIn('title', model_admin.search_fields)
        self.assertIn(RatingInline, model_admin.inlines)

