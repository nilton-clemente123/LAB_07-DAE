import shutil
import tempfile
from datetime import datetime

from django.contrib import admin
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Article, Author, Category

# GIF mínimo de 1×1 para probar la imagen destacada sin crear ficheros reales
TINY_GIF = (
    b'GIF89a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00'
    b'\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)


class ModelTestCase(TestCase):
    """Comprueba __str__, relaciones y orden de los modelos."""

    def setUp(self):
        self.author = Author.objects.create(name='Laura Méndez')
        self.categoria = Category.objects.create(name='Tecnología', slug='tecnologia')
        self.antigua = Article.objects.create(
            title='Noticia antigua', slug='noticia-antigua',
            body='Cuerpo antiguo.', author=self.author,
            published_at=timezone.make_aware(datetime(2026, 1, 10, 9, 0)),
        )
        self.nueva = Article.objects.create(
            title='Noticia nueva', slug='noticia-nueva',
            body='Cuerpo nuevo.', author=self.author,
            published_at=timezone.make_aware(datetime(2026, 3, 15, 10, 30)),
        )
        self.nueva.categories.add(self.categoria)

    def test_str_de_los_modelos(self):
        self.assertEqual(str(self.nueva), 'Noticia nueva')
        self.assertEqual(str(self.categoria), 'Tecnología')
        self.assertEqual(str(self.author), 'Laura Méndez')

    def test_orden_descendente_por_fecha(self):
        self.assertEqual(list(Article.objects.all()), [self.nueva, self.antigua])

    def test_relaciones(self):
        # Article → Category (M2M con related_name='articles')
        self.assertEqual(list(self.categoria.articles.all()), [self.nueva])
        # Article → Author (FK con related_name='articles'; ordering por -published_at)
        self.assertEqual(list(self.author.articles.all()), [self.nueva, self.antigua])

    def test_get_absolute_url(self):
        self.assertEqual(
            self.nueva.get_absolute_url(),
            reverse('news:article_detail', args=['noticia-nueva']),
        )
        self.assertEqual(
            self.categoria.get_absolute_url(),
            reverse('news:category_list', args=['tecnologia']),
        )


class HomeViewTest(TestCase):
    """Portada: bucle for, empty, filtros de fecha y de recorte, {% url %}."""

    def setUp(self):
        self.author = Author.objects.create(name='Carlos Ruiz')
        self.categoria = Category.objects.create(name='Deportes', slug='deportes')
        self.articulo = Article.objects.create(
            title='Noticia de portada', slug='noticia-de-portada',
            body=' '.join(f'palabra{i}' for i in range(1, 41)),
            author=self.author,
            published_at=timezone.make_aware(datetime(2026, 3, 15, 10, 30)),
        )
        self.articulo.categories.add(self.categoria)

    def test_portada_lista_las_noticias(self):
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['articles']), [self.articulo])

    def test_portada_sin_noticias_muestra_el_caso_empty(self):
        self.articulo.delete()
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, 'No hay noticias publicadas todavía.')

    def test_portada_usa_el_fragmento_article_card(self):
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, 'class="card"')
        self.assertContains(response, 'card-summary')

    def test_portada_aplica_el_filtro_de_fecha(self):
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, '15/03/2026')  # published_at|date:"d/m/Y"

    def test_portada_aplica_el_filtro_de_recorte(self):
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, '…')             # truncatewords añade elipsis
        self.assertNotContains(response, 'palabra40')  # el resumen queda recortado

    def test_portada_enlaza_con_etiqueta_url(self):
        response = self.client.get(reverse('news:home'))
        detalle = reverse('news:article_detail', args=[self.articulo.slug])
        categoria = reverse('news:category_list', args=[self.categoria.slug])
        self.assertContains(response, f'href="{detalle}"')
        self.assertContains(response, f'href="{categoria}"')
        self.assertContains(response, f'href="{reverse("news:home")}"')

    def test_portada_carga_la_hoja_de_estilos_con_static(self):
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, '/static/css/styles.css')


class ArticleDetailViewTest(TestCase):
    """Detalle: hereda de base, muestra imagen, autor y categorías."""

    def setUp(self):
        # Carpeta temporal para la imagen destacada del test
        self.media_root = tempfile.mkdtemp(prefix='news_test_media_')
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

        self.author = Author.objects.create(name='Laura Méndez')
        self.categoria = Category.objects.create(name='Cultura', slug='cultura')
        self.articulo = Article.objects.create(
            title='Noticia con detalle', slug='noticia-con-detalle',
            body='Cuerpo completo de la noticia de detalle.',
            author=self.author,
        )
        self.articulo.categories.add(self.categoria)
        self.articulo.image.save('portada.gif', ContentFile(TINY_GIF))
        self.url = reverse('news:article_detail', args=[self.articulo.slug])

    def test_detalle_devuelve_200_y_hereda_de_base(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/article_detail.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_detalle_muestra_imagen_autor_y_categorias(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.articulo.image.url)
        self.assertContains(response, 'Laura Méndez')
        self.assertContains(
            response, reverse('news:category_list', args=['cultura']),
        )
        self.assertContains(response, 'Cuerpo completo de la noticia de detalle.')

    def test_detalle_inexistente_da_404(self):
        response = self.client.get(reverse('news:article_detail', args=['no-existe']))
        self.assertEqual(response.status_code, 404)


class CategoryViewTest(TestCase):
    """Listado por categoría: reutiliza el fragmento de tarjeta."""

    def setUp(self):
        self.author = Author.objects.create(name='Carlos Ruiz')
        self.deportes = Category.objects.create(name='Deportes', slug='deportes')
        self.cultura = Category.objects.create(name='Cultura', slug='cultura')
        self.una = Article.objects.create(
            title='Noticia de deportes', slug='noticia-de-deportes',
            body='Resumen de la noticia de deportes.', author=self.author,
        )
        self.una.categories.add(self.deportes)
        self.otra = Article.objects.create(
            title='Noticia de cultura', slug='noticia-de-cultura',
            body='Resumen de la noticia de cultura.', author=self.author,
        )
        self.otra.categories.add(self.cultura)

    def test_listado_solo_muestra_las_noticias_de_la_categoria(self):
        response = self.client.get(reverse('news:category_list', args=['deportes']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['articles']), [self.una])
        self.assertContains(response, 'Noticia de deportes')
        self.assertNotContains(response, 'Noticia de cultura')

    def test_listado_sin_noticias_muestra_el_caso_empty(self):
        self.otra.delete()
        response = self.client.get(reverse('news:category_list', args=['cultura']))
        self.assertContains(response, 'No hay noticias en esta categoría todavía.')

    def test_listado_reutiliza_el_fragmento_article_card(self):
        response = self.client.get(reverse('news:category_list', args=['deportes']))
        self.assertTemplateUsed(response, 'news/category_list.html')
        self.assertTemplateUsed(response, 'news/_article_card.html')
        self.assertContains(response, 'class="card"')

    def test_categoria_inexistente_da_404(self):
        response = self.client.get(reverse('news:category_list', args=['no-existe']))
        self.assertEqual(response.status_code, 404)


class EscapadoAutomaticoTest(TestCase):
    """Paso 12: el HTML del cuerpo se muestra como texto, no como marcado."""

    def setUp(self):
        self.author = Author.objects.create(name='Laura Méndez')
        self.articulo = Article.objects.create(
            title='Noticia con HTML', slug='noticia-con-html',
            body='<h1>Titular con etiquetas</h1> y <script>alert("xss")</script>',
            author=self.author,
        )
        self.url = reverse('news:article_detail', args=[self.articulo.slug])

    def test_el_detalle_escapa_las_etiquetas_html(self):
        response = self.client.get(self.url)
        # Se muestra literalmente como texto: &lt;h1&gt;...
        self.assertContains(response, '&lt;h1&gt;Titular con etiquetas&lt;/h1&gt;')
        # Y nunca se inyecta el marcado real en el HTML de la página
        self.assertNotContains(response, '<h1>Titular con etiquetas</h1>')
        self.assertNotContains(response, '<script>alert("xss")</script>')

    def test_la_portada_tambien_escapa_el_resumen(self):
        response = self.client.get(reverse('news:home'))
        self.assertNotContains(response, '<script>alert("xss")</script>')
        self.assertContains(response, '&lt;script&gt;')


class AdminRegistrationTest(TestCase):
    """Paso 11: registro y personalización del administrador de las 3 entidades."""

    def test_las_tres_entidades_estan_registradas(self):
        for model in (Article, Category, Author):
            self.assertTrue(admin.site.is_registered(model))

    def test_article_admin_personalizado(self):
        model_admin = admin.site._registry[Article]
        self.assertIn('title', model_admin.list_display)
        self.assertIn('categories', model_admin.list_filter)
        self.assertIn('title', model_admin.search_fields)

    def test_category_admin_personalizado(self):
        model_admin = admin.site._registry[Category]
        self.assertIn('name', model_admin.list_display)
        self.assertIn('name', model_admin.list_filter)
        self.assertIn('name', model_admin.search_fields)

    def test_author_admin_personalizado(self):
        model_admin = admin.site._registry[Author]
        self.assertIn('name', model_admin.list_display)
        self.assertIn('name', model_admin.list_filter)
        self.assertIn('name', model_admin.search_fields)



