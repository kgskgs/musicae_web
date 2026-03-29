from django import template
from django.utils.html import escape, mark_safe
from modeltranslation.utils import build_localized_fieldname


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
        _invert(name) for name in _format_people(publication.authors.all(), publication.language or "")
    )
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
    return _join_citation(
        mla_authors(publication.authors.all(), pub_lang),
        _title_fragment(publication),
        _mla_tail(publication),
    )


@register.simple_tag
def chicago_citation_html(publication, pub_lang: str):
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
