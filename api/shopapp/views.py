"""
В этом модуле лежат обычные наборы представлений.

Рзные view интернет-магазина: по товарам, заказам и т.д.
"""
import logging
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.serializers import serialize
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from timeit import default_timer
from csv import DictWriter
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Product, Order, ProductImage
from .forms import GroupForm
from .forms import ProductForm
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer, OrderSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .common import save_csv_products, save_json_orders
from django.utils.decorators import method_decorator
from django.core.cache import cache

log = logging.getLogger(__name__)


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор предсталений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        print("products list called")
        return super().list(*args, **kwargs)


    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment;filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        methods=["post"],
        detail=False,
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["user", "products"]
    filterset_fields = [
        "delivery_address",
        "products",
        "user",
    ]
    ordering_fields = [
        "delivery_address",
        "products",
        "user",
    ]


class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1312),
            ('Desktop', 2324),
            ('Smartphone', 3284),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 1,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        print("shop index context", context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'form': GroupForm(),
            'groups': Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("products_list")

    # def form_valid(self, form):
    #     form.instance.created_by = self.request.user
    #     return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    # def test_func(self):
    #     product = self.get_object()
    #     user = self.request.user
    #     return user.is_superuser or (user.has_perm('shopapp.change_product') and product.created_by == user)

    def get_success_url(self):
        return reverse(
            "products_details",
            kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )


class OrderCreateView(CreateView):
    model = Order
    fields = 'delivery_address', 'promocode', 'user', 'products'
    success_url = reverse_lazy("orders_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = 'delivery_address', 'promocode', 'user', 'products'
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "order_details",
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
        cache.set(cache_key, products_data, 300)
        elem = products_data[0]
        name = elem["name"]
        print("name: ", name)
        return JsonResponse({"products": products_data})


class OrdersDataExportView(UserPassesTestMixin, View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [p.pk for p in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})

    def test_func(self):
        user = self.request.user
        return user.is_staff


class LatestProductsFeed(Feed):
    title = "Latest products"
    description = "Updates on changes and additions to products"
    link = reverse_lazy('products_list')

    def items(self):
        return (
            Product.objects
            .filter(created_at__isnull=False)
            .order_by('-created_at')[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/user_orders_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.owner = user
        return Order.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.owner
        return context


class UserOrdersExportView(View):
    def get(self, request, user_id):
        cache_key = f'user_orders_export_{user_id}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse(cached_data, safe=False)

        user = get_object_or_404(User, id=user_id)
        orders = Order.objects.filter(user=user).order_by('id')
        serialized_orders = serialize('json', orders)

        cache.set(cache_key, serialized_orders, 300)

        return JsonResponse(serialized_orders, safe=False)