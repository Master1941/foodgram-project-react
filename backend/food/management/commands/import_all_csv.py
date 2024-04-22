from django.core.management.base import BaseCommand, CommandError

from food.management.commands import (import_author_csv,
                                      import_ingredients_csv,
                                      import_recipe_csv,
                                      import_recipe_ingredients_csv,
                                      import_recipe_tags_csv, import_tags_csv)


class Command(BaseCommand):
    help = "Imports all data from CSV files"

    def handle(self, *args, **options):
        try:
            import_tags_csv.Command().handle()
            import_ingredients_csv.Command().handle()
            import_author_csv.Command().handle()
            import_recipe_csv.Command().handle()
            import_recipe_ingredients_csv.Command().handle()
            import_recipe_tags_csv.Command().handle()
            msg = "All data imported successfully"
            self.stdout.write(self.style.SUCCESS(msg))
        except Exception as e:
            raise CommandError(f"Error importing data: {e}")
