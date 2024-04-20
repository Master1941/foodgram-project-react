import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from food.models import Recipe
from foodgram import settings

DATA_ROOT = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    help = "Imports Ingredient data from a CSV file"

    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(DATA_ROOT,"recipe.csv"),
                "r",
                encoding="utf-8",
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        recipe, created = Recipe.objects.get_or_create(
                            id=row["id"],
                            author_id=row["author"],
                            name=row["name"],
                            image=row["image"],
                            text=row["text"],
                            cooking_time=row["cooking_time"],
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(f'recipe "{recipe.name}" создан')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'recipe "{recipe.name}" уже существуют'
                                )
                            )
                    except IntegrityError:
                        self.stdout.write(
                            self.style.ERROR(
                                f"""recipe "{row["name"]}" не удалось
                                    добавить, так как он уже существует"""
                            )
                        )

        except Exception as e:
            raise CommandError(f"Error importing recipe data: {e}")
