import json
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from musicae_content.models import Person, Publication


class Command(BaseCommand):
    help = "Import or update chapter publications from a prepared manifest."

    def add_arguments(self, parser):
        parser.add_argument("manifest_path", help="Path to the generated JSON manifest.")
        parser.add_argument(
            "--overwrite-assets",
            action="store_true",
            help="Replace already attached PDF and banner files when the manifest is imported again.",
        )

    def _assign_translated_value(self, instance, base_field, values):
        base_value = values.get("bg", "")
        setattr(instance, base_field, base_value)
        for lang_code, value in values.items():
            translated_field = f"{base_field}_{lang_code}"
            if hasattr(instance, translated_field):
                setattr(instance, translated_field, value)

    def _save_asset(self, instance, field_name, asset_path, overwrite_assets):
        asset_path = Path(asset_path)
        if not asset_path.exists():
            raise CommandError(f"Asset file not found: {asset_path}")

        field = getattr(instance, field_name)
        current_name = field.name or ""
        current_basename = Path(current_name).name if current_name else ""
        if current_basename == asset_path.name and current_name and not overwrite_assets:
            return

        if current_name and overwrite_assets:
            field.delete(save=False)

        with asset_path.open("rb") as handle:
            field.save(asset_path.name, File(handle), save=False)

    @transaction.atomic
    def handle(self, *args, **options):
        manifest_path = Path(options["manifest_path"]).resolve()
        if not manifest_path.exists():
            raise CommandError(f"Manifest not found: {manifest_path}")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        author_names = manifest.get("author_names_bg") or []
        authors = list(Person.objects.filter(name__in=author_names))
        if len(authors) != len(author_names):
            found = {author.name for author in authors}
            missing = [name for name in author_names if name not in found]
            raise CommandError(f"Missing author records: {', '.join(missing)}")

        overwrite_assets = options["overwrite_assets"]
        created_count = 0
        updated_count = 0

        for entry in manifest.get("entries", []):
            publication = Publication.objects.filter(
                title=entry["title_bg"],
                published_year=entry["published_year"],
            ).first()
            created = publication is None
            if created:
                publication = Publication(
                    title=entry["title_bg"],
                    published_year=entry["published_year"],
                )

            publication.ptype = Publication.ptypes.chapter
            publication.published_year = entry["published_year"]
            publication.published_place = entry["published_place"]
            publication.publisher_txt = entry["publisher_txt"]
            publication.journal_txt = ""
            publication.container_title = entry["container_title"]
            publication.page_range = entry["page_range"]
            publication.language = entry["language"]
            publication.internal = bool(entry.get("internal", False))
            publication.bib_info = entry["bib_info"]

            self._assign_translated_value(
                publication,
                "title",
                {
                    "bg": entry["title_bg"],
                    "en": entry["title_en"],
                    "de": entry["title_de"],
                },
            )
            self._assign_translated_value(
                publication,
                "abstract",
                {
                    "bg": entry["abstract_bg"],
                    "en": entry["abstract_en"],
                    "de": entry["abstract_de"],
                },
            )

            self._save_asset(publication, "file", entry["file_path"], overwrite_assets)
            self._save_asset(publication, "banner", entry["banner_path"], overwrite_assets)

            publication.save()
            publication.authors.set(authors)

            if created:
                created_count += 1
            else:
                updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Updated'} publication: {entry['title_en']}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {created_count} created, {updated_count} updated."
            )
        )
