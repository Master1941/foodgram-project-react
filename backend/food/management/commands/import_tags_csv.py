from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from food.models import Tag
import csv

# import os
# from foodgram import settings


class Command(BaseCommand):
    help = "Imports Ingredient data from a CSV file"

    # def add_arguments(self, parser):
    #     parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        try:
            with open("../data/tags.csv", "r", encoding="utf-8") as file:
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
                                self.style.SUCCESS(f'tags "{tags.name}" создан')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'tags "{tags.name}" уже существуют')
                            )
                    except IntegrityError:
                        self.stdout.write(
                            self.style.ERROR(f'tags "{row["name"]}" не удалось добавить, так как он уже существует')
                        )

        except Exception as e:
            raise CommandError(f"Error importing tags data: {e}")
