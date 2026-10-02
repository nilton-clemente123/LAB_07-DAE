from datetime import timedelta
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from news.models import Article, Author, Category


class Command(BaseCommand):
    help = 'Carga 3 categorías, 2 autores y 6 noticias con imagen destacada (una con HTML en el cuerpo).'

    # Título, categorías, autor, días atrás, color RGB de la imagen
    ARTICLES = [
        (
            'La IA generativa transforma la industria del software',
            ['Tecnología'], 'Laura Méndez', 1, (29, 53, 87),
            'Las empresas de tecnología adoptan asistentes basados en modelos de '
            'lenguaje para acelerar el desarrollo de software. Los equipos aseguran '
            'que la herramienta no sustituye al programador, sino que le ayuda con '
            'tareas repetitivas como la documentación y las pruebas unitarias.',
        ),
        (
            'Nuevo modelo de lenguaje supera récords de precisión',
            ['Tecnología'], 'Laura Méndez', 2, (69, 123, 157),
            'El nuevo modelo supera las marcas anteriores en pruebas de comprensión '
            'y de razonamiento. El equipo de investigación ha publicado el informe '
            'completo con la metodología empleada y los conjuntos de datos utilizados.',
        ),
        (
            'El equipo local se clasifica para la final',
            ['Deportes'], 'Carlos Ruiz', 3, (230, 57, 70),
            'Con un gol en el minuto ochenta y nueve, el equipo local se asegura el '
            'pase a la final del campeonato. La afición celebró el resultado en la '
            'plaza mayor hasta pasada la medianoche.',
        ),
        (
            'Récord de asistencia en el estadio municipal',
            ['Deportes'], 'Carlos Ruiz', 5, (244, 162, 97),
            'El estadio municipal batió su récord de asistencia con más de veinte '
            'mil espectadores. El club ha anunciado medidas de accesibilidad y más '
            'tasas para los próximos partidos de la temporada.',
        ),
        (
            'El festival de cine anuncia su programación',
            ['Cultura'], 'Laura Méndez', 4, (60, 60, 60),
            '<h1>¡Sesenta películas en diez días!</h1> El festival de cine '
            'independiente presenta su programación más ambiciosa, con retrospectivas, '
            'estrenos y encuentros con directores. <strong>Las entradas ya están '
            'disponibles</strong> en la web del certamen y en las taquillas del teatro.',
        ),
        (
            'Una exposición de diseño recorre cien años de cartelería',
            ['Cultura', 'Tecnología'], 'Carlos Ruiz', 6, (42, 157, 143),
            'La muestra reúne más de doscientos carteles originales desde los años '
            'veinte hasta la actualidad. El recorrido incluye una sala dedicada a la '
            'cartelería digital y a los formatos de las pantallas modernas.',
        ),
    ]

    def handle(self, *args, **options):
        now = timezone.now()

        # 1) Categorías
        categories = {}
        for name in ('Tecnología', 'Deportes', 'Cultura'):
            category, _ = Category.objects.get_or_create(
                name=name, defaults={'slug': slugify(name)},
            )
            categories[name] = category

        # 2) Autores
        authors = {}
        for name, bio in (
            ('Laura Méndez', 'Redactora de tecnología y cultura.'),
            ('Carlos Ruiz', 'Redactor de deportes y cultura.'),
        ):
            author, _ = Author.objects.get_or_create(name=name, defaults={'bio': bio})
            authors[name] = author

        # 3) Seis noticias con imagen destacada
        for title, cat_names, author_name, days_ago, color, body in self.ARTICLES:
            slug = slugify(title)
            article, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'body': body,
                    'author': authors[author_name],
                    'published_at': now - timedelta(days=days_ago),
                },
            )
            if not created:
                article.title = title
                article.body = body
                article.author = authors[author_name]
                article.published_at = now - timedelta(days=days_ago)
                article.save()
            article.categories.set(categories[name] for name in cat_names)
            if not article.image:
                article.image.save(
                    f'{slug}.png', self._make_image(color), save=False,
                )
                article.save()

        self.stdout.write(self.style.SUCCESS(
            'Datos de prueba cargados: 3 categorías, 2 autores y 6 noticias '
            '(una con etiquetas HTML en el cuerpo).'
        ))

    @staticmethod
    def _make_image(color):
        """Genera una imagen destacada de 800×450 con Pillow."""
        from PIL import Image, ImageDraw

        img = Image.new('RGB', (800, 450), color)
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 380, 800, 450], fill=(29, 53, 87))
        draw.rectangle([0, 0, 799, 449], outline=(255, 255, 255), width=4)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return ContentFile(buffer.getvalue())
