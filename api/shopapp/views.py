from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, reverse
from timeit import default_timer
from .models import Product, Order
from .forms import ProductForm, OrderForm


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


def groups_list(request: HttpRequest):
    context = {
        'groups': Group.objects.prefetch_related("permissions").all(),
    }
    return render(request, 'shopapp/groups-list.html', context=context)


def products_list(request: HttpRequest):
    context = {
        'products': Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)


def orders_list(request: HttpRequest):
    context = {
        'orders': Order.objects.select_related("user").prefetch_related("products"),
    }
    return render(request, 'shopapp/orders-list.html', context=context)


def create_product(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data['name']
            # price = form.cleaned_data['price']
            # Product.objects.create(**form.cleaned_data)/
            form.save()
            url = reverse("products_list")
            return redirect(url)
    else:
        form = ProductForm()

    context = {
        "form": form
    }

    return render(request, 'shopapp/create-product.html', context=context)


def create_order(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            url = reverse("orders_list")
            return redirect(url)
    else:
        form = OrderForm()

    context = {
        "form": form
    }

    return render(request, 'shopapp/create-order.html', context=context)
