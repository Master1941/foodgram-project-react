import csv
from django.core.management.base import BaseCommand, CommandError
from food.models import Tag, Recipe


class Command(BaseCommand):
    """ "Добавление пользователей из recipe_tags.csv"""

    help = "Добавление пользователей из recipe_tags.csv"

    def handle(self, *args, **options):
        try:
            with open("../data/recipe_tags.csv", "r", encoding="utf-8") as file:
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
                    # except Recipe.DoesNotExist:
                    #     raise CommandError(
                    #         f"Recipe с идентификатором {row['recipe_id']} не существует"
                    #     )
                    # self.stdout.write(
                    #     self.style.SUCCESS(
                    #         "Данные модели Tag, Recipe успешно загружены"
                    #     )
                    # )
        except Exception as e:
            raise CommandError(f"Ошибка при загрузке данных из CSV:  {e}")
