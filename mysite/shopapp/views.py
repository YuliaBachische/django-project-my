from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from timeit import default_timer
# Create your views here.


def shop_index(request: HttpRequest):
    products = [
        ('Laptop', 1312),
        ('Desktop', 2324),
        ('Smartphone', 3284),
    ]
    context = {
        "time_running": default_timer(),
        "products": products,
    }
    return render(request, 'shopapp/shop-index.html', context=context)