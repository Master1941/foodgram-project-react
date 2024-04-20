import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

User = get_user_model()

DATA_ROOT = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    help = "Imports Ingredient data from a CSV file"

    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(DATA_ROOT, "author.csv"),
                "r",
                encoding="utf-8",
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        author, _ = User.objects.get_or_create(
                            id=row["id"],
                            username=row["username"],
                            email=row["email"],
                            first_name=row["first_name"],
                            last_name=row["last_name"],
                        )
                        msg = f'author "{author.username}" создан'
                        self.stdout.write(self.style.SUCCESS(msg))
                    except IntegrityError:
                        self.stdout.write(
                            self.style.ERROR(
                                f"""author "{row["name"]}" не удалось
                                 добавить,
                                 так как он уже существует"""
                            )
                        )
        except Exception as e:
            raise CommandError(f"Error importing author data: {e}")
