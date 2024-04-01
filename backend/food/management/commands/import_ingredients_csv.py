from django.core.management.base import BaseCommand, CommandError
from food.models import Ingredient
import csv


class Command(BaseCommand):
    help = 'Imports Ingredient data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        try:
            with open(options['file_path'], 'r', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=row['name'],
                        measurement_unit=row['measurement_unit'],
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Ингредиент "{ingredient.name}" создан'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Ингредиент "{ingredient.name}" уже существуют'))

        except Exception as e:
            raise CommandError(f'Error importing ingredient data: {e}')
