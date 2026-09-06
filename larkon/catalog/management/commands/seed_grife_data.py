from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Alias legado para seed_vakaria_data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Redirecionando para o novo comando: seed_vakaria_data"))
        call_command("seed_vakaria_data", *args, **options)
