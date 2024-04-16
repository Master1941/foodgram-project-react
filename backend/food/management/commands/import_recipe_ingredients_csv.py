import csv

from django.core.management.base import BaseCommand, CommandError

from food.models import RecipeIngredient


class Command(BaseCommand):
    help = "Добавление пользователей из genre_title.csv"

    def handle(self, *args, **options):

        with open(
            "../data/recipe_ingredients.csv",
            "r",
            encoding="utf-8",
        ) as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    recipe, created = RecipeIngredient.objects.get_or_create(
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

                except ValueError:
                    raise CommandError(
                        "Amount must be a valid floating-point number",
                    )
