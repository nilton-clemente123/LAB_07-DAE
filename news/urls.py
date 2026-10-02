from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    # Las tres páginas del portal, con nombre propio para usar {% url %}
    path('', views.home, name='home'),
    path('categoria/<slug:slug>/', views.category_list, name='category_list'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
]
