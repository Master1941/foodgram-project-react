import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from food.models import Recipe, Tag

DATA_ROOT = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    help = "Добавление пользователей из recipe_tags.csv"

    def handle(self, *args, **options):
        with open(
            os.path.join(DATA_ROOT, "recipe_tags.csv"),
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
