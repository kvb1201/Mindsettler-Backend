from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = "Create superuser if not exists (Render-safe)"

    def handle(self, *args, **options):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        username = os.getenv("DJANGO_SUPERUSER_NAME", "admin")

        if not email or not password:
            self.stdout.write("Superuser env vars not set. Skipping.")
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write("Superuser already exists. Skipping.")
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            username=username if hasattr(User, "username") else None,
        )

        self.stdout.write("✅ Superuser created successfully.")