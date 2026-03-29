from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from .admin import PublicationAdmin
from .models import Person, Publication
from .templatetags.citations import (
    build_bibtex,
    build_ris,
    chicago_citation_html,
    mla_citation_html,
)


class PublicationCitationTests(TestCase):
    def _make_author(self, name, **translations):
        author = Person.objects.create(name=name, member=False)
        for field_name, value in translations.items():
            if hasattr(author, field_name):
                setattr(author, field_name, value)
        if translations:
            author.save()
        return author

    def _make_publication(self, **overrides):
        defaults = {
            "ptype": Publication.ptypes.art,
            "title": "Untitled publication",
            "published_year": 2024,
            "journal_txt": "",
            "publisher_txt": "",
            "published_place": "",
            "page_range": "",
            "language": "en",
        }
        defaults.update(overrides)
        return Publication.objects.create(**defaults)

    def test_article_citations_and_exports_include_page_range(self):
        author = self._make_author("Ada Lovelace")
        publication = self._make_publication(
            title="Counterpoint in Motion",
            journal_txt="Journal of Musical Inquiry",
            publisher_txt="Fundamenta Press",
            page_range=" 10 - 24 ",
        )
        publication.authors.add(author)

        mla = str(mla_citation_html(publication, "en"))
        chicago = str(chicago_citation_html(publication, "en"))
        bibtex = build_bibtex(publication, "https://example.com/publications/1/")
        ris = build_ris(publication, "https://example.com/publications/1/")

        self.assertIn("Lovelace, Ada.", mla)
        self.assertIn("&ldquo;Counterpoint in Motion.&rdquo;", mla)
        self.assertIn("Journal of Musical Inquiry, 2024, pp. 10-24.", mla)

        self.assertIn("&ldquo;Counterpoint in Motion.&rdquo;", chicago)
        self.assertIn("Journal of Musical Inquiry (2024): 10-24.", chicago)

        self.assertIn("@article{pub", bibtex)
        self.assertIn("journal = {Journal of Musical Inquiry}", bibtex)
        self.assertIn("pages = {10-24}", bibtex)
        self.assertIn("url = {https://example.com/publications/1/}", bibtex)

        self.assertIn("TY  - JOUR", ris)
        self.assertIn("SP  - 10", ris)
        self.assertIn("EP  - 24", ris)
        self.assertIn("UR  - https://example.com/publications/1/", ris)

    def test_book_citations_keep_standalone_title_format(self):
        author = self._make_author("Nadia Boulanger")
        publication = self._make_publication(
            ptype=Publication.ptypes.mon,
            title="Modes of Thought",
            publisher_txt="Cambridge University Press",
            published_place="Cambridge",
            page_range="1-250",
        )
        publication.authors.add(author)

        mla = str(mla_citation_html(publication, "en"))
        chicago = str(chicago_citation_html(publication, "en"))
        bibtex = build_bibtex(publication, "https://example.com/publications/2/")
        ris = build_ris(publication, "https://example.com/publications/2/")

        self.assertIn("<em>Modes of Thought</em>.", mla)
        self.assertIn("Cambridge University Press, 2024.", mla)
        self.assertNotIn("pp.", mla)

        self.assertIn("<em>Modes of Thought</em>.", chicago)
        self.assertIn("Cambridge: Cambridge University Press, 2024.", chicago)

        self.assertIn("@book{pub", bibtex)
        self.assertNotIn("pages = {", bibtex)

        self.assertIn("TY  - BOOK", ris)
        self.assertNotIn("SP  - ", ris)

    def test_chapter_citations_and_exports_use_book_container_data(self):
        first_author = self._make_author(
            "Емил Деведжиев",
            name_en="Emil Devedjiev",
            name_de="Emil Devedjiev",
        )
        second_author = self._make_author(
            "Кристиан Василев",
            name_en="Christian Vassilev",
            name_de="Christian Vassilev",
        )
        publication = self._make_publication(
            ptype=Publication.ptypes.chapter,
            title="Behaviorism, Development, Education",
            container_title="Music Development and Music Education",
            publisher_txt="Riva",
            published_place="Sofia",
            page_range="35-54",
        )
        publication.authors.add(first_author, second_author)

        mla = str(mla_citation_html(publication, "en"))
        chicago = str(chicago_citation_html(publication, "en"))
        bibtex = build_bibtex(publication, "https://example.com/publications/3/")
        ris = build_ris(publication, "https://example.com/publications/3/")

        self.assertIn("Devedjiev, Emil, and Christian Vassilev.", mla)
        self.assertIn("<em>Music Development and Music Education</em>.", mla)
        self.assertIn("Riva, 2024.", mla)
        self.assertNotIn("Behaviorism, Development, Education", mla)
        self.assertNotIn("35-54", mla)

        self.assertIn("Devedjiev, Emil, and Christian Vassilev.", chicago)
        self.assertIn("<em>Music Development and Music Education</em>.", chicago)
        self.assertIn("Sofia: Riva, 2024.", chicago)
        self.assertNotIn("Behaviorism, Development, Education", chicago)
        self.assertNotIn("35-54", chicago)

        self.assertIn("@book{pub", bibtex)
        self.assertIn("title = {Music Development and Music Education}", bibtex)
        self.assertIn("author = {Devedjiev, Emil and Vassilev, Christian}", bibtex)
        self.assertIn("publisher = {Riva}", bibtex)
        self.assertIn("address = {Sofia}", bibtex)
        self.assertNotIn("pages = {35-54}", bibtex)
        self.assertNotIn("Behaviorism, Development, Education", bibtex)

        self.assertIn("TY  - BOOK", ris)
        self.assertIn("TI  - Music Development and Music Education", ris)
        self.assertIn("AU  - Devedjiev, Emil", ris)
        self.assertIn("AU  - Vassilev, Christian", ris)
        self.assertIn("PB  - Riva", ris)
        self.assertIn("CY  - Sofia", ris)
        self.assertNotIn("SP  - 35", ris)
        self.assertNotIn("EP  - 54", ris)

    def test_publication_detail_page_renders_page_range_and_downloads(self):
        author = self._make_author("Clara Schumann")
        publication = self._make_publication(
            title="Form and Memory",
            journal_txt="Studies in Form",
            page_range="33-48",
        )
        publication.authors.add(author)

        response = self.client.get(publication.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Цитирай")
        self.assertContains(response, "33-48")
        self.assertContains(response, "Studies in Form")
        self.assertContains(response, "Download BibTeX")
        self.assertContains(response, "Download RIS")

    def test_same_year_publications_order_by_first_page_then_title(self):
        first = self._make_publication(
            ptype=Publication.ptypes.chapter,
            title="First chapter",
            published_year=2021,
            page_range="7-34",
        )
        second = self._make_publication(
            ptype=Publication.ptypes.chapter,
            title="Second chapter",
            published_year=2021,
            page_range="35-54",
        )
        third = self._make_publication(
            title="Standalone publication",
            published_year=2021,
            page_range="",
        )

        publications = list(Publication.objects.filter(published_year=2021))

        self.assertEqual([publication.pk for publication in publications], [first.pk, second.pk, third.pk])
        self.assertEqual(first.sort_page_start, 7)
        self.assertEqual(second.sort_page_start, 35)
        self.assertEqual(third.sort_page_start, 999999)


class PublicationBibtexImportTests(TestCase):
    def setUp(self):
        self.admin = PublicationAdmin(Publication, AdminSite())

    def test_import_maps_page_range_and_publication_type(self):
        entry = {
            "ENTRYTYPE": "inproceedings",
            "title": "On Polyphonic Memory",
            "year": "2023",
            "booktitle": "Proceedings of the Modal Congress",
            "publisher": "Fundamenta Press",
            "address": "Sofia",
            "pages": "55--61",
            "author": "Doe, Jane and Smith, John",
        }

        publication, created, status = self.admin.create_publication_from_entry(entry)

        self.assertTrue(created)
        self.assertEqual(status, "created")
        self.assertEqual(publication.ptype, Publication.ptypes.doc)
        self.assertEqual(publication.container_title, "Proceedings of the Modal Congress")
        self.assertEqual(publication.journal_txt, "")
        self.assertEqual(publication.publisher_txt, "Fundamenta Press")
        self.assertEqual(publication.published_place, "Sofia")
        self.assertEqual(publication.page_range, "55-61")
        self.assertEqual(publication.authors.count(), 2)

    def test_import_maps_incollection_to_chapter(self):
        entry = {
            "ENTRYTYPE": "incollection",
            "title": "Listening and Development",
            "year": "2021",
            "booktitle": "Music Development and Music Education",
            "publisher": "Riva",
            "address": "Sofia",
            "pages": "117--134",
            "author": "Devedjiev, Emil and Vassilev, Christian",
        }

        publication, created, status = self.admin.create_publication_from_entry(entry)

        self.assertTrue(created)
        self.assertEqual(status, "created")
        self.assertEqual(publication.ptype, Publication.ptypes.chapter)
        self.assertEqual(publication.container_title, "Music Development and Music Education")
        self.assertEqual(publication.publisher_txt, "Riva")
        self.assertEqual(publication.page_range, "117-134")
