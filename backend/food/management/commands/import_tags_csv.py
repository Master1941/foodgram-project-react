import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from food.models import Tag

DATA_ROOT = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    help = "Imports Ingredient data from a CSV file"

    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(DATA_ROOT, "tags.csv"),
                "r",
                encoding="utf-8",
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        tags, created = Tag.objects.get_or_create(
                            id=row["id"],
                            name=row["name"],
                            color=row["color"],
                            slug=row["slug"],
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'tags "{tags.name}" создан'
                                )
                            )
                    except IntegrityError:
                        self.stdout.write(
                            self.style.ERROR(
                                f"""tags "{row["name"]}" не удалось
                                  добавить, так как он уже существует"""
                            )
                        )
        except Exception as e:
            raise CommandError(f"Error importing tags data: {e}")
