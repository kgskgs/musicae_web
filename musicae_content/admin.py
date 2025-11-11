from django import forms
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages

from modeltranslation.admin import TranslationAdmin, TranslationStackedInline
from modeltranslation.utils import get_translation_fields
from ckeditor.widgets import CKEditorWidget
from django.utils.html import format_html


from .models import (
    Person,
    Publication,
    pTopic,
    pKeyword,
    Publisher,
    Journal,
    Link,
    File,
    ResearchSection,
    ResearchPage
)

import bibtexparser


# ---------- Helper Mixin ----------

class TranslatedCKEditorFormMixin:
    """Attach CKEditor to translated text fields automatically."""
    richtext_fields = []  # override in subclass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for base_field in self.richtext_fields:
            # Attach CKEditor to all translation variants of that field
            for lang_field in [f for f in self.fields if f.startswith(base_field)]:
                self.fields[lang_field].widget = CKEditorWidget()


# ---------- Custom Forms ----------

class PersonAdminForm(TranslatedCKEditorFormMixin, forms.ModelForm):
    richtext_fields = ["bio", "currentResearch"]

    class Meta:
        model = Person
        fields = "__all__"


class PublicationAdminForm(TranslatedCKEditorFormMixin, forms.ModelForm):
    richtext_fields = ["abstract", "bib_info"]

    class Meta:
        model = Publication
        fields = "__all__"


class BibTeXImportForm(forms.Form):
    bib_file = forms.FileField(
        label="BibTeX File (.bib)",
        help_text="Upload a .bib file to import publications."
    )


# ---------- Admins ----------

class PersonAdmin(TranslationAdmin):
    form = PersonAdminForm
    ordering = ("position",)
    list_display = ["name", "pk", "position", "member", "orcid_link"]
    search_fields = ("name", "title", "bio", "currentResearch", "orcid")
    list_filter = ("member",)

    def orcid_link(self, obj):
        if obj.orcid:
            return format_html('<a href="https://orcid.org/{}" target="_blank">{}</a>', obj.orcid, obj.orcid)
        return "-"
    orcid_link.short_description = "ORCID"

    def get_fieldsets(self, request, obj=None):
        base_fieldsets = super().get_fieldsets(request, obj)
        fieldsets = []
        for name, opts in base_fieldsets:
            fields = []
            for f in opts.get("fields", []):
                fields.append(f)
                # Add translation fields for multilingual content
                if f in ("bio", "currentResearch", "name", "title"):
                    fields += get_translation_fields(f)
            fieldsets.append((name, {"fields": tuple(fields)}))

        # ✅ Add ORCID if not already in the fieldsets
        # You can also control where it appears
        if not any("orcid" in fs[1]["fields"] for fs in fieldsets):
            fieldsets[0][1]["fields"] += ("orcid",)

        return fieldsets

class PublicationAdmin(TranslationAdmin):
    form = PublicationAdminForm
    ordering = ("-published_year",)
    save_as = True

    list_display = ["title", "internal", "ptype", "published_year", "pk"]
    list_filter = ("ptype", "published_year", "internal")
    search_fields = ("title", "abstract", "bib_info")
    filter_horizontal = ("authors",)

    fieldsets = (
        (None, {
            "fields": (
                "ptype",
                "title",
                "abstract",
                "published_year",
                "published_place",
                "bib_info",
                "language",
                "internal",
                "authors",
                "publisher_txt",
                "journal_txt",
                "topic",
                "keywords_txt",
                "file",
                "banner", 
            )
        }),
    )

    # ----- BibTeX Import Integration -----

    def get_urls(self):
        """
        Add custom URL for BibTeX import.
        """
        urls = super().get_urls()
        my_urls = [
            path(
                "import-bibtex/",
                self.admin_site.admin_view(self.import_bibtex_view),
                name="publication_import_bibtex",
            ),
        ]
        return my_urls + urls

    def import_bibtex_view(self, request):
        """
        Custom view: upload and process a .bib file.
        """
        if request.method == "POST":
            form = BibTeXImportForm(request.POST, request.FILES)
            if form.is_valid():
                bib_file = form.cleaned_data["bib_file"]

                try:
                    bib_content = bib_file.read().decode("utf-8")
                    # Using loads for bibtexparser 1.x compatibility
                    bib_database = bibtexparser.loads(bib_content)
                except Exception as e:
                    self.message_user(
                        request,
                        f"Error parsing BibTeX file: {e}",
                        level=messages.ERROR,
                    )
                    return redirect("admin:musicae_content_publication_changelist")

                created_count = 0
                updated_count = 0
                skipped_count = 0

                for entry in bib_database.entries:
                    try:
                        pub, created, status = self.create_publication_from_entry(entry)
                        if status == "created":
                            created_count += 1
                        elif status == "updated":
                            updated_count += 1
                        else:
                            skipped_count += 1
                    except Exception as e:
                        print(f"Failed to import entry '{entry.get('title')}': {e}")
                        skipped_count += 1

                self.message_user(
                    request,
                    f"Import complete: {created_count} created, "
                    f"{updated_count} updated, {skipped_count} skipped.",
                    level=messages.SUCCESS,
                )
                return redirect("admin:musicae_content_publication_changelist")
        else:
            form = BibTeXImportForm()

        context = dict(
            self.admin_site.each_context(request),
            title="Import BibTeX",
            form=form,
            opts=self.model._meta,
        )
        return render(request, "admin/publication_import_bibtex.html", context)

    # ----- BibTeX Helpers & Mapping -----

    def _get_first_nonempty(self, entry, *keys):
        """
        Return the first non-empty BibTeX value for any of the given keys.
        Handles strings, lists, and strips common BibTeX braces.
        """
        for key in keys:
            if key in entry:
                value = entry[key]
                # If parser returns list/tuple, join it
                if isinstance(value, (list, tuple)):
                    value = " ".join(str(v) for v in value if v)
                elif not isinstance(value, str):
                    value = str(value)

                cleaned = value.strip().replace("{", "").replace("}", "").strip()
                if cleaned:
                    return cleaned
        return None

    def create_publication_from_entry(self, entry):
        """
        Parse a single BibTeX entry (dict) and map it to the Publication model.
        Deduplicate by (title, year). Fill journal_txt, publisher_txt, published_place, keywords_txt.
        """

        # --- Title ---
        raw_title = entry.get("title")
        if raw_title:
            title = (
                str(raw_title)
                .replace("{", "")
                .replace("}", "")
                .replace("\n", " ")
            )
            title = " ".join(title.split()).strip()
        else:
            return (None, False, "skipped")

        # --- Year ---
        year_str = entry.get("year") or entry.get("date")
        if not year_str:
            return (None, False, "skipped")

        year_str = str(year_str).strip().strip("{}")
        if len(year_str) >= 4 and year_str[:4].isdigit():
            year = int(year_str[:4])
        else:
            return (None, False, "skipped")

        # --- Map BibTeX -> our text fields ---

        # journal: journal / journaltitle / booktitle
        journal_txt = self._get_first_nonempty(entry, "journal", "journaltitle", "booktitle")

        # publisher: publisher / organization / institution
        publisher_txt = self._get_first_nonempty(entry, "publisher", "organization", "institution")

        # place: address / location
        published_place = self._get_first_nonempty(entry, "address", "location")

        # abstract
        abstract = self._get_first_nonempty(entry, "abstract")

        # keywords: normalize ; to ,
        raw_keywords = self._get_first_nonempty(entry, "keywords", "keyword")
        if raw_keywords:
            keywords_txt = raw_keywords.replace(";", ",")
        else:
            keywords_txt = None

        # --- Get or create by (title, year) ---

        try:
            pub, created = Publication.objects.get_or_create(
                title__iexact=title,
                published_year=year,
                defaults={
                    "title": title,
                    "published_year": year,
                    "published_place": published_place or "",
                    "abstract": abstract or "",
                    "journal_txt": journal_txt or "",
                    "publisher_txt": publisher_txt or "",
                    "keywords_txt": keywords_txt or "",
                },
            )
        except Exception as e:
            print(f"Error in get_or_create for '{title}': {e}")
            return (None, False, "skipped")

        status = "created" if created else "updated"

        # --- Update ONLY missing fields on existing records ---

        if not created:
            changed = False

            if published_place and not pub.published_place:
                pub.published_place = published_place
                changed = True

            if abstract and not pub.abstract:
                pub.abstract = abstract
                changed = True

            if journal_txt and not pub.journal_txt:
                pub.journal_txt = journal_txt
                changed = True

            if publisher_txt and not pub.publisher_txt:
                pub.publisher_txt = publisher_txt
                changed = True

            if keywords_txt and not pub.keywords_txt:
                pub.keywords_txt = keywords_txt
                changed = True

            if changed:
                status = "updated"

        # --- Authors ---
        author_objs = []
        author_string = entry.get("author")

        if author_string:
            # Basic "Author One and Author Two" splitting
            names = [n.strip() for n in str(author_string).split(" and ") if n.strip()]
            for full_name in names:
                person, _ = Person.objects.get_or_create(name=full_name)
                author_objs.append(person)

        pub.save()

        if author_objs:
            pub.authors.set(author_objs)

        return (pub, created, status)

class LinkAdmin(admin.ModelAdmin):
    list_display = ["url"]


class FileAdmin(admin.ModelAdmin):
    list_display = ["title", "get_file_url"]


class SectionForm(forms.ModelForm):
    class Meta:
        model = ResearchSection
        fields = "__all__"
        widgets = {
            "body": CKEditorWidget(),  # modeltranslation clones this to body_<lang>
        }

class ResearchSectionInline(TranslationStackedInline):
    model = ResearchSection
    form = SectionForm
    extra = 1                # shows a blank inline — the “+” flow you want
    show_change_link = True
    fields = (
        "order", "title", "body", "person",
    )
    ordering = ("order", "id")

@admin.register(ResearchPage)
class ResearchPageAdmin(admin.ModelAdmin):
    inlines = [ResearchSectionInline]
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug", "parent", "menu_order", "show_in_menu", "template")
    list_filter  = ("parent", "show_in_menu", "template")
    search_fields = ("name", "slug")
    fields = ("name", "slug", "parent", "show_in_menu", "menu_order", "template")


@admin.register(pKeyword)
class PKeywordAdmin(TranslationAdmin):
    list_display = ("text",)
    search_fields = ("text",)

@admin.register(pTopic)
class PTopicAdmin(TranslationAdmin):
    list_display = ("text",)
    search_fields = ("text",)

# admin.py
from modeltranslation.admin import TranslationAdmin




# ---------- Registration ----------

admin.site.register(Person, PersonAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Publisher)
admin.site.register(Journal)
admin.site.register(Link, LinkAdmin)
admin.site.register(File, FileAdmin)