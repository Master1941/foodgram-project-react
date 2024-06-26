import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from food.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    help = "Imports Ingredient data from a CSV file"

    def handle(self, *args, **options):
        with open(
            os.path.join(DATA_ROOT, "ingredients.csv"),
            "r",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=row["name"],
                        measurement_unit=row["measurement_unit"],
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Ингредиент "{ingredient.name}" создан'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'''Ингредиент "{ingredient.name}"
                                  уже существуют'''
                            )
                        )

                except Exception as e:
                    raise CommandError(f"Error importing ingredient data: {e}")
