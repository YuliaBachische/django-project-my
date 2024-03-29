from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from string import ascii_letters
from random import choices
from django.conf import settings
from .models import Product, Order
from .utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("create_product"),
            {
                "name": self.product_name,
                "price": "2345.67",
                "description": "Cool laptop",
                "discount": "12"

            },
            HTTP_USER_AGENT='Mozilla/5.0'
        )
        self.assertRedirects(response, reverse("products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Test Product")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("products_details", kwargs={"pk": self.product.pk}),
            HTTP_USER_AGENT='Mozilla/5.0'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("products_details", kwargs={"pk": self.product.pk}),
            HTTP_USER_AGENT='Mozilla/5.0'
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'product-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse("products_list"), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='testpass')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("orders_list"), HTTP_USER_AGENT='Mozilla/5')
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("orders_list"), HTTP_USER_AGENT='Mozilla/5')
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures =[
        'product-fixture.json'
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse("products-export"),
            HTTP_USER_AGENT='Mozilla/5'
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data
        )


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='testpass')
        permission_order = Permission.objects.get(
            codename='view_order'
        )
        cls.user.user_permissions.add(permission_order)

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address='test delivery address',
            promocode='test promocode',
            user=self.user,
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse("order_details",  kwargs={"pk": self.order.pk}),
            HTTP_USER_AGENT='Mozilla/5'
        )
        self.assertContains(response, "test delivery address")
        self.assertContains(response, "test promocode")
        self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportViewTestCase(TestCase):
    fixtures =[
        'user-fixture.json',
        'product-fixture.json',
        'order-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='testpass')
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_orders_view(self):
        response = self.client.get(
            reverse("orders-export"),
            HTTP_USER_AGENT='Mozilla/5'
        )
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [p.pk for p in order.products.all()],
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(
            orders_data["orders"],
            expected_data
        )