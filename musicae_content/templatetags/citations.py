from django import template
from modeltranslation.utils import build_localized_fieldname

register = template.Library()

def _norm(lang: str) -> str:
    if not lang:
        return ""
    l = lang.strip().lower()
    if l.startswith("bg"):  # bg or bg-BG
        return "bg"
    if "-" in l:
        l = l.split("-", 1)[0]
    return l

def _display_name_for_lang(person, pub_lang: str) -> str:
    """Use native for bg, else use translated name (exact lang -> en -> base)."""
    if not person:
        return ""
    lang = _norm(pub_lang)
    if lang == "bg":
        return getattr(person, "name", "") or ""
    # exact language field (e.g., name_de)
    field_exact = build_localized_fieldname("name", lang)
    if hasattr(person, field_exact):
        v = getattr(person, field_exact) or ""
        if v:
            return v
    # preferred latinized fallback: English
    field_en = build_localized_fieldname("name", "en")
    if hasattr(person, field_en):
        v = getattr(person, field_en) or ""
        if v:
            return v
    return getattr(person, "name", "") or ""

def _split_given_family(fullname: str):
    """
    Best-effort split:
    - If there's a comma, assume 'Family, Given...'
    - Else last token is family, the rest is given
    """
    if not fullname:
        return ("", "")
    s = fullname.strip()
    if "," in s:
        fam, given = s.split(",", 1)
        return (given.strip(), fam.strip())
    parts = s.split()
    if len(parts) == 1:
        return ("", parts[0])  # given empty, family only
    return (" ".join(parts[:-1]), parts[-1])

def _invert(fullname: str) -> str:
    given, family = _split_given_family(fullname)
    if family and given:
        return f"{family}, {given}"
    return fullname  # fallback

@register.filter
def inverted_name_for_lang(person, pub_lang: str):
    """Family, First for a single person, respecting publication language."""
    return _invert(_display_name_for_lang(person, pub_lang))

@register.filter
def name_for_lang(person, pub_lang: str):
    """Normal order (Given Family) for a single person, respecting language."""
    return _display_name_for_lang(person, pub_lang)

@register.simple_tag
def mla_authors(authors, pub_lang: str):
    """
    MLA 9 quick rules:
    - 1 author: invert (Family, First)
    - 2 authors: invert first; second normal order; join with ', and '
    - 3+ authors: invert first + 'et al.'
    """
    people = list(authors)
    n = len(people)
    if n == 0:
        return ""
    if n == 1:
        return inverted_name_for_lang(people[0], pub_lang)
    if n == 2:
        first = inverted_name_for_lang(people[0], pub_lang)
        second = name_for_lang(people[1], pub_lang)
        return f"{first}, and {second}"
    first = inverted_name_for_lang(people[0], pub_lang)
    return f"{first}, et al."

@register.simple_tag
def chicago_authors(authors, pub_lang: str):
    """
    Chicago (bibliography) quick rules:
    - 1 author: invert first
    - 2 authors: invert first; second normal; join with ', and '
    - 3–10 authors: invert first; others normal separated by ', '; Oxford comma before 'and'
    - >10 authors: list first seven (same pattern) + ', et al.'
    """
    people = list(authors)
    n = len(people)
    if n == 0:
        return ""
    if n == 1:
        return inverted_name_for_lang(people[0], pub_lang)
    if n == 2:
        first = inverted_name_for_lang(people[0], pub_lang)
        second = name_for_lang(people[1], pub_lang)
        return f"{first}, and {second}"
    # 3 or more
    limit = 10
    shown = people[:min(n, limit if n <= 10 else 7)]
    first = inverted_name_for_lang(shown[0], pub_lang)
    rest = [name_for_lang(p, pub_lang) for p in shown[1:]]
    if n > 10:
        return f"{first}, {', '.join(rest)}, et al."
    # 3–10: Oxford comma before 'and'
    if len(rest) == 1:
        return f"{first}, and {rest[0]}"
    return f"{first}, {', '.join(rest[:-1])}, and {rest[-1]}"
