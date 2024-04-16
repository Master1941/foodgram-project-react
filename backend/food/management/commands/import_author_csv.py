import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = "Imports Ingredient data from a CSV file"

    # def add_arguments(self, parser):
    #     parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        try:
            with open("../data/author.csv", "r", encoding="utf-8") as file:
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

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'author "{author.username}" создан'
                            )
                        )

                    except IntegrityError:
                        self.stdout.write(
                            self.style.ERROR(
                                f'''author "{row["name"]}" не удалось
                                 добавить,
                                 так как он уже существует'''
                            )
                        )

        except Exception as e:
            raise CommandError(f"Error importing author data: {e}")
