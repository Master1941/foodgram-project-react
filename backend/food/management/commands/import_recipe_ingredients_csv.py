import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from food.models import RecipeIngredient

DATA_ROOT = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    help = "Добавление пользователей из genre_title.csv"

    def handle(self, *args, **options):

        with open(
            os.path.join(DATA_ROOT, "recipe_ingredients.csv"),
            "r",
            encoding="utf-8",
        ) as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    recipe, created = RecipeIngredient.objects.get_or_create(
                        # id=row["id"],
                        amount=float(row["amount"]),
                        recipe_id=row["recipe_id"],
                        ingredient_id=row["ingredient_id"],
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'recipe "{recipe.amount}" создан',
                            )
                        )
                except IntegrityError:
                    self.stdout.write(
                        self.style.ERROR(
                            f"""RecipeIngredient "{row["recipe_id"]}" не удалось
                                 добавить,
                                 так как он уже существует"""
                        )
                    )
                except ValueError:
                    raise CommandError(
                        "Amount must be a valid floating-point number",
                    )
