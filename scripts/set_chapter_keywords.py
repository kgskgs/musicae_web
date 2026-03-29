from musicae_content.models import Publication


MAPPING = {
    "Увод": "психология, музика, музикално развитие, музикално образование, педагогика",
    "Търсене на всеобщи познавателни структури": "психология, музика, познание, когниция, структури",
    "Бихейвиоризъм, развитие, образование": "психология, музика, бихейвиоризъм, учене, образователни стратегии",
    "Когнитивни теории на музикалното развитие": "психология, музика, когнитивни теории, развитие, модели",
    "Музикално възприятие в ранните периоди на развитие": "психология, музика, възприятие, ранно детство, слухово развитие",
    "Музикална енкултурация": "психология, музика, енкултурация, социализация, културни практики",
    "Музикална компетенция и музикално умение": "психология, музика, компетентност, умение, изпълнение",
    "Музикална и езикова способност": "психология, музика, език, способности, интердисциплинарност",
    "Музика и емоция": "психология, музика, емоции, афект, експресивност",
}


updated = 0
missing = []
for title, keywords in MAPPING.items():
    publication = Publication.objects.filter(title=title).first()
    if not publication:
        missing.append(title)
        continue
    publication.keywords_txt = keywords
    publication.save(update_fields=["keywords_txt"])
    updated += 1

print(f"Updated publications: {updated}")
if missing:
    print("Missing publications:")
    for title in missing:
        print(f"- {title}")

for publication in Publication.objects.filter(title__in=MAPPING.keys()).order_by("sort_page_start"):
    print(f"{publication.title} => {publication.keywords_txt}")
