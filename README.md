# DAE LAB 07 — Panel de administración de cine con Django

Proyecto de la sesión: gestión de **películas**, **géneros**, **personas** (dirección
y reparto) y **valoraciones**, con un panel de administración personalizado y una
**vista pública de recomendaciones**.

## Requisitos

- Python 3.11
- Django 5.2
- Pillow (para el campo de imagen `poster` de `Movie`)

## Puesta en marcha

```powershell
python -m pip install django pillow

# Migraciones y datos de prueba
python manage.py migrate
python manage.py setup_users          # superusuario + grupo «editores» + editor
python manage.py load_sample_data     # 4 géneros, 10 películas, valoraciones en 6

python manage.py runserver            # http://127.0.0.1:8000/
```

- **Panel de administración:** http://127.0.0.1:8000/admin/
- **Vista pública:** http://127.0.0.1:8000/  (recomendaciones en `/recomendaciones/<id>/`)

## Credenciales de prueba

| Usuario   | Contraseña        | Rol / permisos                                    |
|-----------|-------------------|---------------------------------------------------|
| `admin`   | `AdminLab07#2026` | Superusuario (acceso total)                       |
| `editor`  | `EditorLab07#2026`| Grupo «editores»: añadir/cambiar películas (sin borrar) |

> Los usuarios se crean con `python manage.py setup_users`.

## Estructura del proyecto

```
DAE LAB 07/
├── manage.py
├── proyecto/                 # Configuración del proyecto
│   ├── settings.py           # INSTALLED_APPS incluye 'movies'; Pillow/idioma/medios
│   └── urls.py               # admin/ + rutas públicas + media en DEBUG
└── movies/                   # Aplicación
    ├── models.py             # Genre, Person, Movie, Rating
    ├── admin.py              # ModelAdmin personalizados + inline de valoraciones
    ├── views.py              # movie_list y recommendations
    ├── urls.py
    ├── templates/movies/     # movie_list.html, recommendations.html
    └── management/commands/  # setup_users.py, load_sample_data.py
```

## 1–2. Modelos

- **Genre** (`name`, único) — relación **muchos a muchos** con `Movie` vía `Movie.genres`.
- **Person** (`name`) — usada como dirección (`Movie.director`, FK) y reparto (`Movie.cast`, M2M).
- **Movie** (`title`, `year`, `poster`, `genres`, `director`, `cast`, `created_at`, `updated_at`).
  - `average_rating` (propiedad) = nota media de sus valoraciones.
- **Rating** (`movie` FK, `value` 1–5, `comment`, `created_at`) — **clave foránea** hacia `Movie`.

Cada modelo define su `Meta` (`ordering`, `verbose_name(_plural)`) y su `__str__`.

## 3. Migraciones y superusuario

```powershell
python manage.py makemigrations movies
python manage.py migrate
python manage.py setup_users   # crea también el superusuario «admin»
```

## 4. Registro simple (estado «antes»)

Sin escribir ninguna vista, el panel ya ofrece las cuatro operaciones (Añadir / Cambiar
/ Borrar / Ver) por cada modelo. El registro simple sería:

```python
from django.contrib import admin
from .models import Genre, Movie, Person, Rating

admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Person)
admin.site.register(Rating)
```

## 5–7. ModelAdmin personalizado (estado «después»)

En `movies/admin.py`:

- **`list_display`**: `title`, `year`, `director`, `genres_list`, `average_rating`.
- **`list_filter`**: por `genres` y `year`.
- **`search_fields`**: por `title`, `director__name` y `cast__name`.
- **Inline** (`RatingInline`): las valoraciones se dan de alta dentro del formulario de
  la película, sin salir del registro padre.
- **`readonly_fields`**: `created_at` y `updated_at` aparecen visibles pero no editables
  (bloque «Auditoría»).

## 8. Datos de prueba

Cargados desde el comando `load_sample_data` (equivale a darlos de alta por el panel):
**10 películas**, **4 géneros** (Acción, Drama, Comedia, Ciencia ficción) y
**valoraciones en 6 películas** (≥ 5, como pide la práctica).

## 9. Grupo «editores»

- Grupo **`editores`** con permisos `add_movie`, `change_movie` y `view_movie`
  (**sin** `delete_movie`).
- Usuario **`editor`** dentro del grupo, con `is_staff=True` y sin `is_superuser`.
- Al entrar con `editor`, el panel muestra **solo «Películas»** (no aparecen Géneros,
  Personas ni Valoraciones) y **desaparece la casilla/acción de borrar**.

