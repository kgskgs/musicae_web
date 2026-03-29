from django.core.management.base import BaseCommand

from musicae_content.models import Publication


TOKEN_MAP = {
    "психология": ("psychology", "psychologie"),
    "музика": ("music", "musik"),
    "музикално развитие": ("music development", "musikalische entwicklung"),
    "музикално образование": ("music education", "musikalische bildung"),
    "педагогика": ("pedagogy", "pädagogik"),
    "познание": ("cognition", "kognition"),
    "когниция": ("cognition", "kognition"),
    "структури": ("structures", "strukturen"),
    "бихейвиоризъм": ("behaviorism", "behaviorismus"),
    "учене": ("learning", "lernen"),
    "образователни стратегии": ("educational strategies", "bildungsstrategien"),
    "когнитивни теории": ("cognitive theories", "kognitive theorien"),
    "развитие": ("development", "entwicklung"),
    "модели": ("models", "modelle"),
    "възприятие": ("perception", "wahrnehmung"),
    "ранно детство": ("early childhood", "frühe kindheit"),
    "слухово развитие": ("auditory development", "auditive entwicklung"),
    "енкултурация": ("enculturation", "enkulturation"),
    "социализация": ("socialization", "sozialisierung"),
    "културни практики": ("cultural practices", "kulturelle praktiken"),
    "компетентност": ("competence", "kompetenz"),
    "умение": ("skill", "fähigkeit"),
    "изпълнение": ("performance", "ausführung"),
    "език": ("language", "sprache"),
    "способности": ("abilities", "fähigkeiten"),
    "интердисциплинарност": ("interdisciplinarity", "interdisziplinarität"),
    "емоции": ("emotions", "emotionen"),
    "афект": ("affect", "affekt"),
    "експресивност": ("expressivity", "expressivität"),
}


def _translate_tokens(tokens, target_lang):
    translated = []
    seen = set()
    for token in tokens:
        normalized = token.casefold()
        pair = TOKEN_MAP.get(normalized)
        if pair:
            candidate = pair[0] if target_lang == "en" else pair[1]
        else:
            candidate = token
        if candidate.casefold() in seen:
            continue
        seen.add(candidate.casefold())
        translated.append(candidate)
    return translated[: Publication.KEYWORDS_MAX_COUNT]


class Command(BaseCommand):
    help = "Backfill multilingual publication keyword fields (BG/EN/DE) from existing keyword data."

    def handle(self, *args, **options):
        updated = 0
        for publication in Publication.objects.all():
            source_raw = getattr(publication, "keywords_txt_bg", None) or publication.keywords_txt
            source_tokens = Publication.parse_keywords(source_raw)

            changed_fields = []
            normalized_language = (publication.language or "").strip().lower()
            should_be_bulgarian = normalized_language.startswith("bg")
            if publication.is_bulgarian != should_be_bulgarian:
                publication.is_bulgarian = should_be_bulgarian
                changed_fields.append("is_bulgarian")

            if source_tokens:
                normalized_bg = ", ".join(source_tokens[: Publication.KEYWORDS_MAX_COUNT])

                if hasattr(publication, "keywords_txt_bg") and not (publication.keywords_txt_bg or "").strip():
                    publication.keywords_txt_bg = normalized_bg
                    changed_fields.append("keywords_txt_bg")

                if hasattr(publication, "keywords_txt_en") and not (publication.keywords_txt_en or "").strip():
                    publication.keywords_txt_en = ", ".join(_translate_tokens(source_tokens, "en"))
                    changed_fields.append("keywords_txt_en")

                if hasattr(publication, "keywords_txt_de") and not (publication.keywords_txt_de or "").strip():
                    publication.keywords_txt_de = ", ".join(_translate_tokens(source_tokens, "de"))
                    changed_fields.append("keywords_txt_de")

            if changed_fields:
                publication.save(update_fields=changed_fields)
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated publications: {updated}"))
