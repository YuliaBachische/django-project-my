from csv import DictReader
from io import TextIOWrapper
import json

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_json_orders(json_data):
    orders = json.loads(json_data.read().decode("utf-8"))

    for order_data in orders:
        product_ids = order_data['products']
        delivery_address = order_data['delivery_address']
        user_id = order_data['user']

        user = get_object_or_404(User, id=user_id)

        order = Order.objects.create(delivery_address=delivery_address, user=user)

        order.products.set(product_ids)

        order.save()

    return orders