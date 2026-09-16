from django.shortcuts import render
from .models import Fabric


def index(request):
    template_name = 'index.html'
    # Берем ткани для витрины на главной
    popular_fabrics = Fabric.objects.filter(show_on_main=True)[:10]

    context = {
        'fabrics': popular_fabrics,
    }
    return render(request, template_name, context)


def fabrics_catalog(request):
    template_name = 'fabrics.html'
    # Показываем все доступные ткани (20-30 штук)
    all_fabrics = Fabric.objects.all()

    context = {
        'fabrics': all_fabrics,
    }
    return render(request, template_name, context)


def about(request):
    template_name = 'about.html'
    context = {}
    return render(request, template_name, context)


def services(request):
    template_name = 'services.html'
    context = {}
    return render(request, template_name, context)


def portfolio(request):
    template_name = 'portfolio.html'
    context = {}
    return render(request, template_name, context)


def process(request):
    template_name = 'process.html'
    context = {}
    return render(request, template_name, context)


def delivery(request):
    template_name = 'delivery.html'
    context = {}
    return render(request, template_name, context)


def contact(request):
    template_name = 'contact.html'
    context = {}
    return render(request, template_name, context)
