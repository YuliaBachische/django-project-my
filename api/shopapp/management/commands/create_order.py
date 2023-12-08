from django.contrib.auth.models import User
from django.core.management import BaseCommand
from ...models import Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Create order')
        user = User.objects.get(username='john')
        order = Order.objects.get_or_create(
            delivery_address='Some adress',
            promocode='somesale',
            user=user,
        )
        self.stdout.write(f'Created order {order}')