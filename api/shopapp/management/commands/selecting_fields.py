from typing import Sequence
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from ...models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('Start demo select fields')
        user_values = User.objects.values_list('username', flat=True)
        print(list(user_values))
        for user in user_values:
            print(user)
        # product_values = Product.objects.values('pk', 'name')
        # for product in product_values:
        #     print(product)
        self.stdout.write(f'Done')