from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.urls import reverse
from django.utils import timezone

import datetime
import os


def forDjango(cls):
    """https://stackoverflow.com/a/35953630/1002899"""
    cls.do_not_call_in_templates = True
    return cls


class pTopic(models.Model):
    text = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.text


class pKeyword(models.Model):
    text = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.text


class Publisher(models.Model):
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Journal(models.Model):
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    currentResearch = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    email = models.EmailField(
        verbose_name="Email Address",
        max_length=254,
        blank=True,
        null=True
    )
    image = models.ImageField(upload_to='members_img/', blank=True)
    member = models.BooleanField()
    position = models.IntegerField(blank=True, null=True)

    # ✅ NEW FIELD
    orcid = models.CharField(
        max_length=19,  # 0000-000X-XXXX-XXXX
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{4}-\d{4}-[\dX]{4}$',
                message='Enter a valid ORCID in the format 0000-000X-XXXX-XXXX'
            )
        ],
        help_text="Enter ORCID in the format 0000-000X-XXXX-XXXX",
    )

    class Meta:
         ordering = ["position", "name"]  

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("members_det", args=[self.pk])

    def orcid_url(self):
        """Returns full ORCID link if available."""
        if self.orcid:
            return f"https://orcid.org/{self.orcid}"
        return None

class Publication(models.Model):
    # Вложеният клас за избор на тип публикация (ptypes), както поискахте
    class ptypes(models.IntegerChoices):
        mon = 0, _("Монография")
        col = 1, _("Сборник")
        dis = 2, _("Дипломен/дисертационен труд")
        aut = 3, _("Автореферат")
        stu = 4, _("Студия")
        art = 5, _("Статия")
        doc = 6, _("Доклад")
        tex = 7, _("Учебник")
        hab = 8, _("Хабилитация")
        onl = 9, _("Онлайн материал")
        elb = 10, _("Електронна книга")

    # Основно съдържание (регистрирано за превод)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    abstract = models.TextField(blank=True, verbose_name=_("Abstract"))
    bib_info = models.TextField(blank=True, verbose_name=_("Bibliographic Info"))
    published_place = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Published Place"))
    
    # Поле за тип публикация, използващо вложения клас
    ptype = models.IntegerField(
        choices=ptypes.choices, 
        default=ptypes.art,
        verbose_name=_("Type")
    )
    
    # --- НОВИ ТЕКСТОВИ ПОЛЕТА (Заместват dropdowns) ---
    publisher_txt = models.CharField(
        max_length=255, 
        verbose_name=_("Publisher (Text)"),
        blank=True, 
        null=True
    )
    journal_txt = models.CharField(
        max_length=255, 
        verbose_name=_("Journal (Text)"),
        blank=True, 
        null=True
    )
    keywords_txt = models.TextField(
        verbose_name=_("Keywords (Comma Separated)"),
        blank=True, 
        null=True,
        help_text=_("Enter keywords as a single block of text, separated by commas.")
    )

    # Други полета
    published_year = models.IntegerField(verbose_name=_("Year"))
    internal = models.BooleanField(default=False, verbose_name=_("Internal Publication"))
    language = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Language"))

    # Полета за връзка (остават dropdowns/multi-selects)
    authors = models.ManyToManyField('Person', related_name='publications', verbose_name=_("Authors"))
    topic = models.ForeignKey('pTopic', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Topic"))

     # NEW: optional banner image
    banner = models.ImageField(
        upload_to='publication_banners/',
        blank=True,
        null=True,
        verbose_name=_("Banner image"),
        help_text=_("Image used in the Recent Publications slider.")
    )

    # Файл
    file = models.FileField(upload_to='publications/', blank=True, null=True, verbose_name=_("File"))

    class Meta:
        verbose_name = _("Publication")
        verbose_name_plural = _("Publications")
        ordering = ['-published_year', 'title']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("publications_det", args=[self.pk])


class Link(models.Model):
    url = models.URLField()
    text = models.TextField(max_length=1000)


class File(models.Model):
    file = models.FileField(upload_to='files/', blank=True)
    title = models.CharField(max_length=255)

    def get_file_url(self):
        return self.file.url
    
class ResearchPage(models.Model):
    name = models.CharField(max_length=100, default="Research")
    slug = models.SlugField(unique=True, default="research")

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    show_in_menu = models.BooleanField(default=True)
    menu_order = models.PositiveIntegerField(default=0)

    # >>> NEW: template selector
    # Set this to whatever you consider the "old template name" in the admin UI.
    BASE_TEMPLATE_LABEL = "Research detail"

    TEMPLATE_CHOICES = [
        ("alt", BASE_TEMPLATE_LABEL),                                   # old/current template
        ("single", f"{BASE_TEMPLATE_LABEL} — Single column"),           # new template label
    ]
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default="alt")

    class Meta:
        ordering = ["menu_order", "name"]
        verbose_name = _("Research page")
        verbose_name_plural = _("Research pages")

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} › {self.name}"
        return self.name

    # Pick the actual template file based on the choice
    def get_template_name(self):
        return {
            "alt": "musicae_content/research_detail.html",                  # existing file
            "single": "musicae_content/research_detail_single_column.html", # new file
        }.get(self.template, "musicae_content/research_detail.html")


class ResearchSection(models.Model):
    page = models.ForeignKey(
    "ResearchPage",
    on_delete=models.CASCADE,
    related_name="sections",
    null=False,
    blank=False,
)
    title = models.CharField(max_length=255, verbose_name=_("Title"), blank=True)
    body = models.TextField(verbose_name=_("Body (HTML allowed)"))
    person = models.ForeignKey(
        "Person", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="research_sections"
    )
    order = models.PositiveIntegerField(
        default=0, help_text=_("Display order (ascending)")
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Research section")
        verbose_name_plural = _("Research sections")

    def __str__(self):
        return f"{self.order:03d} • {self.title}"
