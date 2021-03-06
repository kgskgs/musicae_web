from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

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

    image = models.ImageField(upload_to='members_img/', blank=True)

    member = models.BooleanField()

    position = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("members_det", args=[self.pk])


class Publication(models.Model):
    added = models.DateTimeField(auto_now_add=True)

    @forDjango
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

    ptype = models.IntegerField(choices=ptypes.choices)
    title = models.CharField(max_length=255)
    abstract = models.TextField(blank=True)
    internal = models.BooleanField()
    authors = models.ManyToManyField(Person,
                                     symmetrical=False, blank=True)

    publisher = models.ForeignKey(Publisher, blank=True,
                                  null=True, on_delete=models.SET_NULL)
    journal = models.ForeignKey(Journal, blank=True,
                                null=True, on_delete=models.SET_NULL)
    published_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.date.today().year)])
    published_place = models.CharField(max_length=255, blank=True)

    topic = models.ForeignKey(pTopic,
                              null=True, on_delete=models.SET_NULL)
    keywords = models.ManyToManyField(pKeyword,
                                      symmetrical=False, blank=True)
    bib_info = models.CharField(max_length=1000, blank=True,
                                null=True)
    language = models.CharField(max_length=255, blank=True,
                                null=True)

    file = models.FileField(upload_to='publications/', blank=True)

    def __str__(self):
        return self.title

    def filename(self):
        return os.path.basename(self.file.name)

    def get_file_url(self):
        return self.file.url

    class Meta:
        ordering = ["-published_year"]
        get_latest_by = "-published_year"

    def get_absolute_url(self):
        return reverse("publications_det", args=[self.pk])


class Seminar(models.Model):
    title = models.CharField(max_length=255)
    time = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    description = models.TextField()

    @forDjango
    class semesters(models.IntegerChoices):
        fal = -1, _('Есенен семестър')
        spr = 1, _('Пролетен семестър')

    semester = models.IntegerField(choices=semesters.choices)
    active = models.BooleanField()

    profs = models.ManyToManyField(Person,
                                   symmetrical=False, blank=True)

    def __str__(self):
        return self.title


class News(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    changed = models.DateField(auto_now_add=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news_img/', blank=True)
    content = models.TextField()

    @forDjango
    class types(models.IntegerChoices):
        new = 1, _('Новини')
        sch = 2, _('Учебна дейност')
        stu = 3, _('Студентска работилница')
        com = 4, _('Коментари и анализи')
        son = 5, _('Fundamenta Musicae in sonis')

    ntype = models.IntegerField(choices=types.choices, default=1)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-added"]
        get_latest_by = "-added"

    def get_absolute_url(self):
        return reverse("news_det", args=[self.pk])


class Link(models.Model):
    url = models.URLField()
    text = models.TextField(max_length=1000)


class File(models.Model):
    file = models.FileField(upload_to='files/', blank=True)
    title = models.CharField(max_length=255)

    def get_file_url(self):
        return self.file.url
