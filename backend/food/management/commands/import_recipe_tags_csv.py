import csv

from django.core.management.base import BaseCommand, CommandError

from food.models import Recipe, Tag


class Command(BaseCommand):
    """ "Добавление пользователей из recipe_tags.csv"""

    help = "Добавление пользователей из recipe_tags.csv"

    def handle(self, *args, **options):
        with open(
            "../data/recipe_tags.csv",
            "r",
            encoding="utf-8",
        ) as file:
            for row in csv.DictReader(file):
                try:
                    tag = Tag.objects.get(pk=row["tags_id"])
                    recipe = Recipe.objects.get(pk=row["recipe_id"])
                    recipe.tags.add(tag)

                    self.stdout.write(
                        self.style.SUCCESS(
                            "Данные модели Tag, Recipe успешно загружены"
                        )
                    )

                except Tag.DoesNotExist:
                    raise CommandError(
                        f"Тег с идентификатором {row['tags_id']} не существует"
                    )
