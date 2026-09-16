from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Это свяжет главную страницу с функцией index
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('fabrics/', views.fabrics_catalog, name='fabrics'),
    path('process/', views.process, name='process'),
    path('delivery/', views.delivery, name='delivery'),
    path('contact/', views.contact, name='contact'),
]
