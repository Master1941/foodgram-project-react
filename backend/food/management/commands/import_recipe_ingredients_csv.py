from django.core.management.base import BaseCommand, CommandError
from food.models import Recipe, Ingredient, RecipeIngredient
import csv


class Command(BaseCommand):
    help = "Добавление пользователей из genre_title.csv"

    def handle(self, *args, **options):
        try:
            with open("../data/recipe_ingredients.csv", "r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    try:
                        # recipe = Recipe.objects.get(pk=row["recipe_id"])
                        # ingredient = Ingredient.objects.get(pk=row["ingredient_id"])
                        # recipe.ingredients.add(ingredient)

                        recipe, created = RecipeIngredient.objects.get_or_create(
                            amount=float(row["amount"]),
                            recipe_id=row["recipe_id"],
                            ingredient_id=row["ingredient_id"],
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(f'recipe "{recipe.amount}" создан')
                            )
                    # except Recipe.DoesNotExist:
                    #     raise CommandError(
                    #         f"Recipe with id {row['recipe_id']} does not exist"
                    #     )
                    # except Ingredient.DoesNotExist:
                    #     raise CommandError(
                    #         f"Ingredient with id {row['ingredient_id']} does not exist"
                    #     )
                    except ValueError:
                        raise CommandError(
                            "Amount must be a valid floating-point number"
                        )

            print("Data for model RecipeIngredient loaded successfully")
        except Exception as e:
            raise CommandError(f"Error loading data from CSV: {e}")
