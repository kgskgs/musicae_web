from django import template
from django.utils.html import escape, mark_safe
from modeltranslation.utils import build_localized_fieldname

from musicae_content.book_chapter_upload_data import (
    AUTHOR_NAMES_BG,
    BOOK_TITLE_BG,
    BOOK_TITLE_DE,
    BOOK_TITLE_EN,
)


register = template.Library()


def _norm(lang: str) -> str:
    if not lang:
        return ""
    normalized = lang.strip().lower()
    if normalized.startswith("bg"):
        return "bg"
    if "-" in normalized:
        normalized = normalized.split("-", 1)[0]
    return normalized


def _display_name_for_lang(person, pub_lang: str) -> str:
    if not person:
        return ""
    lang = _norm(pub_lang)
    if lang == "bg":
        return getattr(person, "name", "") or ""

    field_exact = build_localized_fieldname("name", lang)
    if hasattr(person, field_exact):
        value = getattr(person, field_exact) or ""
        if value:
            return value

    field_en = build_localized_fieldname("name", "en")
    if hasattr(person, field_en):
        value = getattr(person, field_en) or ""
        if value:
            return value

    return getattr(person, "name", "") or ""


def _bg_name(person) -> str:
    if not person:
        return ""

    field_bg = build_localized_fieldname("name", "bg")
    if hasattr(person, field_bg):
        value = getattr(person, field_bg) or ""
        if value:
            return value

    raw_value = person.__dict__.get("name")
    if raw_value:
        return raw_value

    return getattr(person, "name", "") or ""


def _split_given_family(fullname: str):
    if not fullname:
        return ("", "")

    value = fullname.strip()
    if "," in value:
        family, given = value.split(",", 1)
        return (given.strip(), family.strip())

    parts = value.split()
    if len(parts) == 1:
        return ("", parts[0])
    return (" ".join(parts[:-1]), parts[-1])


def _invert(fullname: str) -> str:
    given, family = _split_given_family(fullname)
    if family and given:
        return f"{family}, {given}"
    return fullname


def _format_people(authors, pub_lang: str):
    return [_display_name_for_lang(person, pub_lang) for person in authors]


def _ordered_people(publication, pub_lang: str):
    people = list(publication.authors.all())
    if publication.ptype != publication.ptypes.chapter:
        return _format_people(people, pub_lang)

    by_bg_name = {
        _bg_name(person).strip(): person
        for person in people
    }
    ordered_people = []
    used_names = set()

    for bg_name in AUTHOR_NAMES_BG:
        person = by_bg_name.get(bg_name)
        if person:
            ordered_people.append(_display_name_for_lang(person, pub_lang))
            used_names.add(bg_name)

    for person in people:
        bg_name = _bg_name(person).strip()
        if bg_name not in used_names:
            ordered_people.append(_display_name_for_lang(person, pub_lang))

    return ordered_people


def _book_title_for_lang(pub_lang: str) -> str:
    lang = _norm(pub_lang)
    if lang == "de":
        return BOOK_TITLE_DE
    if lang == "en":
        return BOOK_TITLE_EN
    return BOOK_TITLE_BG


def _join_citation(authors: str, title_html: str, tail: str):
    pieces = []
    if authors:
        pieces.append(f"{escape(authors)}.")
    if title_html:
        pieces.append(title_html)
    if tail:
        pieces.append(tail)
    return mark_safe(" ".join(piece for piece in pieces if piece))


def _title_fragment(publication):
    title = escape(publication.title or "")
    if publication.citation_title_is_quoted:
        return f"&ldquo;{title}.&rdquo;"
    return f"<em>{title}</em>."


def _page_range(publication):
    if not publication.supports_page_range:
        return ""
    return publication.normalized_page_range


def _mla_tail(publication):
    year = str(publication.published_year) if publication.published_year else ""
    pages = _page_range(publication)
    container = publication.citation_container
    publisher = publication.citation_publisher
    place = publication.citation_place

    if publication.citation_kind == "chapter":
        bits = []
        if container:
            bits.append(f"<em>{escape(container)}</em>")
        if publisher:
            bits.append(escape(publisher))
        if year:
            bits.append(escape(year))
        if pages:
            bits.append(f"pp. {escape(pages)}")
        return f"{', '.join(bits)}." if bits else ""

    if publication.citation_kind == "container":
        bits = []
        if container:
            bits.append(escape(container))
        elif publisher:
            bits.append(escape(publisher))
        if year:
            bits.append(escape(year))
        if pages:
            bits.append(f"pp. {escape(pages)}")
        return f"{', '.join(bits)}." if bits else ""

    if publication.citation_kind == "thesis":
        bits = []
        institution = publisher or container or place
        if institution:
            bits.append(escape(institution))
        if year:
            bits.append(escape(year))
        return f"{', '.join(bits)}." if bits else ""

    bits = []
    if publisher:
        bits.append(escape(publisher))
    elif place:
        bits.append(escape(place))
    if year:
        bits.append(escape(year))
    return f"{', '.join(bits)}." if bits else ""


def _chicago_tail(publication):
    year = str(publication.published_year) if publication.published_year else ""
    pages = _page_range(publication)
    container = publication.citation_container
    publisher = publication.citation_publisher
    place = publication.citation_place

    if publication.citation_kind == "chapter":
        prefix = f"In <em>{escape(container)}</em>" if container else ""
        if prefix and pages and place and publisher and year:
            return f"{prefix}, {escape(pages)}. {escape(place)}: {escape(publisher)}, {escape(year)}."
        if prefix and pages:
            return f"{prefix}, {escape(pages)}."
        if prefix and place and publisher and year:
            return f"{prefix}. {escape(place)}: {escape(publisher)}, {escape(year)}."
        if place and publisher and year:
            return f"{escape(place)}: {escape(publisher)}, {escape(year)}."
        return prefix + "." if prefix else ""

    if publication.citation_kind == "container":
        if container and year and pages:
            return f"{escape(container)} ({escape(year)}): {escape(pages)}."
        if container and year:
            return f"{escape(container)} ({escape(year)})."
        if container and pages:
            return f"{escape(container)}: {escape(pages)}."

        bits = []
        if publisher:
            bits.append(escape(publisher))
        if year:
            bits.append(escape(year))
        if pages:
            bits.append(f"pp. {escape(pages)}")
        return f"{', '.join(bits)}." if bits else ""

    if publication.citation_kind == "thesis":
        institution = publisher or container
        if place and institution and year:
            return f"{escape(place)}: {escape(institution)}, {escape(year)}."
        if institution and year:
            return f"{escape(institution)}, {escape(year)}."
        if place and year:
            return f"{escape(place)}, {escape(year)}."
        if year:
            return f"{escape(year)}."
        return ""

    if place and publisher and year:
        return f"{escape(place)}: {escape(publisher)}, {escape(year)}."
    if publisher and year:
        return f"{escape(publisher)}, {escape(year)}."
    if place and year:
        return f"{escape(place)}, {escape(year)}."
    if year:
        return f"{escape(year)}."
    return ""


def _bibtex_escape(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def _split_page_range(page_range: str):
    if not page_range:
        return ("", "")
    parts = page_range.split("-", 1)
    if len(parts) == 2:
        return (parts[0].strip(), parts[1].strip())
    return (page_range.strip(), "")


def build_bibtex(publication, url: str = "") -> str:
    key = f"pub{publication.pk or 'draft'}"
    authors = " and ".join(
        _invert(name) for name in _ordered_people(publication, publication.language or "")
    )

    if publication.ptype == publication.ptypes.chapter:
        fields = [
            ("title", _book_title_for_lang(publication.language or "")),
            ("author", authors),
            ("year", publication.published_year),
            ("publisher", publication.citation_publisher),
            ("address", publication.citation_place),
        ]
        if publication.language:
            fields.append(("language", publication.language))
        if url:
            fields.append(("url", url))

        body = ",\n".join(
            f"  {name} = {{{_bibtex_escape(value)}}}"
            for name, value in fields
            if value not in (None, "")
        )
        return f"@book{{{key},\n{body}\n}}"

    fields = [
        ("title", publication.title),
        ("author", authors),
        ("year", publication.published_year),
    ]

    secondary_field = publication.bibtex_secondary_title_field
    if secondary_field and publication.citation_container:
        fields.append((secondary_field, publication.citation_container))

    if publication.bibtex_entry_type == "phdthesis" and publication.citation_publisher:
        fields.append(("school", publication.citation_publisher))
    elif publication.citation_publisher:
        fields.append(("publisher", publication.citation_publisher))

    if publication.citation_place and publication.bibtex_entry_type != "article":
        fields.append(("address", publication.citation_place))

    if publication.supports_page_range:
        fields.append(("pages", publication.normalized_page_range))

    if publication.language:
        fields.append(("language", publication.language))

    if url:
        fields.append(("url", url))

    body = ",\n".join(
        f"  {name} = {{{_bibtex_escape(value)}}}"
        for name, value in fields
        if value not in (None, "")
    )
    return f"@{publication.bibtex_entry_type}{{{key},\n{body}\n}}"


def build_ris(publication, url: str = "") -> str:
    if publication.ptype == publication.ptypes.chapter:
        lines = [
            "TY  - BOOK",
            f"TI  - {_book_title_for_lang(publication.language or '')}",
        ]

        for author in _ordered_people(publication, publication.language or ""):
            lines.append(f"AU  - {_invert(author)}")

        if publication.published_year:
            lines.append(f"PY  - {publication.published_year}")

        if publication.citation_publisher:
            lines.append(f"PB  - {publication.citation_publisher}")

        if publication.citation_place:
            lines.append(f"CY  - {publication.citation_place}")

        if publication.language:
            lines.append(f"LA  - {publication.language}")

        if url:
            lines.append(f"UR  - {url}")

        lines.append("ER  -")
        return "\n".join(lines)

    lines = [
        f"TY  - {publication.ris_reference_type}",
        f"TI  - {publication.title}",
    ]

    for author in _format_people(publication.authors.all(), publication.language or ""):
        lines.append(f"AU  - {_invert(author)}")

    if publication.published_year:
        lines.append(f"PY  - {publication.published_year}")

    if publication.citation_container:
        lines.append(f"T2  - {publication.citation_container}")

    if publication.citation_publisher:
        lines.append(f"PB  - {publication.citation_publisher}")

    if publication.citation_place:
        lines.append(f"CY  - {publication.citation_place}")

    if publication.supports_page_range:
        start_page, end_page = _split_page_range(publication.normalized_page_range)
        if start_page:
            lines.append(f"SP  - {start_page}")
        if end_page:
            lines.append(f"EP  - {end_page}")

    if publication.language:
        lines.append(f"LA  - {publication.language}")

    if url:
        lines.append(f"UR  - {url}")

    lines.append("ER  -")
    return "\n".join(lines)


@register.filter
def inverted_name_for_lang(person, pub_lang: str):
    return _invert(_display_name_for_lang(person, pub_lang))


@register.filter
def name_for_lang(person, pub_lang: str):
    return _display_name_for_lang(person, pub_lang)


@register.simple_tag
def mla_authors(authors, pub_lang: str):
    people = _format_people(list(authors), pub_lang)
    count = len(people)
    if count == 0:
        return ""
    if count == 1:
        return _invert(people[0])
    if count == 2:
        return f"{_invert(people[0])}, and {people[1]}"
    return f"{_invert(people[0])}, et al."


@register.simple_tag
def chicago_authors(authors, pub_lang: str):
    people = _format_people(list(authors), pub_lang)
    count = len(people)
    if count == 0:
        return ""
    if count == 1:
        return _invert(people[0])
    if count == 2:
        return f"{_invert(people[0])}, and {people[1]}"

    shown = people[:7] if count > 10 else people[:10]
    first = _invert(shown[0])
    rest = shown[1:]
    if count > 10:
        return f"{first}, {', '.join(rest)}, et al."
    if len(rest) == 1:
        return f"{first}, and {rest[0]}"
    return f"{first}, {', '.join(rest[:-1])}, and {rest[-1]}"


@register.simple_tag
def mla_citation_html(publication, pub_lang: str):
    if publication.ptype == publication.ptypes.chapter:
        authors = _ordered_people(publication, pub_lang)
        count = len(authors)
        if count == 0:
            author_text = ""
        elif count == 1:
            author_text = _invert(authors[0])
        elif count == 2:
            author_text = f"{_invert(authors[0])}, and {authors[1]}"
        else:
            author_text = f"{_invert(authors[0])}, et al."

        return _join_citation(
            author_text,
            f"<em>{escape(_book_title_for_lang(pub_lang))}</em>.",
            f"{escape(publication.citation_publisher)}, {escape(publication.published_year)}."
            if publication.citation_publisher and publication.published_year
            else "",
        )

    return _join_citation(
        mla_authors(publication.authors.all(), pub_lang),
        _title_fragment(publication),
        _mla_tail(publication),
    )


@register.simple_tag
def chicago_citation_html(publication, pub_lang: str):
    if publication.ptype == publication.ptypes.chapter:
        authors = _ordered_people(publication, pub_lang)
        count = len(authors)
        if count == 0:
            author_text = ""
        elif count == 1:
            author_text = _invert(authors[0])
        elif count == 2:
            author_text = f"{_invert(authors[0])}, and {authors[1]}"
        else:
            shown = authors[:7] if count > 10 else authors[:10]
            first = _invert(shown[0])
            rest = shown[1:]
            if count > 10:
                author_text = f"{first}, {', '.join(rest)}, et al."
            elif len(rest) == 1:
                author_text = f"{first}, and {rest[0]}"
            else:
                author_text = f"{first}, {', '.join(rest[:-1])}, and {rest[-1]}"

        tail = ""
        if publication.citation_place and publication.citation_publisher and publication.published_year:
            tail = (
                f"{escape(publication.citation_place)}: "
                f"{escape(publication.citation_publisher)}, {escape(publication.published_year)}."
            )
        elif publication.citation_publisher and publication.published_year:
            tail = f"{escape(publication.citation_publisher)}, {escape(publication.published_year)}."

        return _join_citation(
            author_text,
            f"<em>{escape(_book_title_for_lang(pub_lang))}</em>.",
            tail,
        )

    return _join_citation(
        chicago_authors(publication.authors.all(), pub_lang),
        _title_fragment(publication),
        _chicago_tail(publication),
    )


@register.simple_tag
def bibtex_citation(publication, url: str = ""):
    return build_bibtex(publication, url)


@register.simple_tag
def ris_citation(publication, url: str = ""):
    return build_ris(publication, url)
