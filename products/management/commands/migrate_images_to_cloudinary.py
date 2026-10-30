from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from products.models import Product


class Command(BaseCommand):
    help = "Upload product images from MEDIA_ROOT to the configured storage."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be uploaded without changing products.",
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.is_dir():
            raise CommandError(f"Media directory does not exist: {media_root}")

        products = Product.objects.exclude(image="").exclude(image__isnull=True)
        uploaded = 0
        missing = 0

        for product in products.iterator():
            filename = Path(product.image.name).name
            source = media_root / filename

            if not source.is_file():
                missing += 1
                self.stderr.write(
                    self.style.WARNING(
                        f"Missing: {filename} (product {product.pk})"
                    )
                )
                continue

            if options["dry_run"]:
                self.stdout.write(f"Would upload: {filename}")
                continue

            with source.open("rb") as image_file:
                product.image.save(filename, File(image_file), save=True)
            uploaded += 1
            self.stdout.write(f"Uploaded: {filename}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed: {uploaded} uploaded, {missing} missing, "
                "0 failed."
            )
        )
