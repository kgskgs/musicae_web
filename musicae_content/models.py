from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

import datetime
import os


def forDjango(cls):
    """https://stackoverflow.com/a/35953630/1002899"""
    cls.do_not_call_in_templates = True
    return cls


class pTopic(models.Model):
    text = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.text


class pKeyword(models.Model):
    text = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.text


class Publisher(models.Model):
    name = models.CharField(max_length=250)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(max_length=5000, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    currentResearch = models.TextField(max_length=5000, blank=True, null=True)
    short_description = models.TextField(max_length=1000, blank=True, null=True)

    image = models.ImageField(upload_to='members_img/', blank=True)

    member = models.BooleanField()

    position = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name


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
        tex = 7, _("Учебник/учебно помагало")

    ptype = models.IntegerField(choices=ptypes.choices)
    title = models.CharField(max_length=250)
    abstract = models.TextField(blank=True)
    internal = models.BooleanField()
    authors = models.ManyToManyField(Person,
                                     symmetrical=False, blank=True)

    publisher = models.ForeignKey(Publisher, blank=True,
                                  null=True, on_delete=models.SET_NULL)
    published_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.date.today().year)])
    published_place = models.CharField(max_length=500, blank=True)

    topic = models.ForeignKey(pTopic,
                              null=True, on_delete=models.SET_NULL)
    keywords = models.ManyToManyField(pKeyword,
                                      symmetrical=False, blank=True)
    bib_info = models.CharField(max_length=500, blank=True,
                                null=True)

    file = models.FileField(upload_to='publications/', blank=True)

    def __str__(self):
        return self.title

    def filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        ordering = ["-published_year"]
        get_latest_by = "-published_year"


class Seminar(models.Model):
    title = models.CharField(max_length=400)
    time = models.CharField(max_length=400)
    place = models.CharField(max_length=400)
    description = models.TextField(max_length=5000)

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
    title = models.CharField(max_length=400)
    image = models.ImageField(upload_to='news_img/', blank=True)
    content = models.TextField(max_length=5000)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-added"]
        get_latest_by = "-added"
