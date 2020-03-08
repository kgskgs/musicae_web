from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class pTopic(models.Model):
    text = models.CharField(max_length=250)

    def __str__(self):
        return self.text


class Publisher(models.Model):
    name = models.CharField(max_length=250)
    website = models.URLField(blank=True)


class Publication(models.Model):

    class ptypes(models.IntegerChoices):
        art = 0, _('Article')
        dis = 1, _('Dissertation')
        ths = 2, _('PhD Thesis')
        bok = 3, _('Book')

    ptype = models.IntegerField(choices=ptypes.choices)

    published = models.DateField()
    added = models.DateTimeField(auto_now_add=True)

    title = models.CharField(max_length=250)
    abstract = models.TextField(blank=True)

    publisher = models.ForeignKey(Publisher, null=True, on_delete=models.SET_NULL)

    published_in = models.CharField(max_length=500, blank=True)
    published_url = models.URLField(blank=True)

    file = models.FileField(upload_to='publications/')

    topics = models.ManyToManyField(pTopic,
                                    symmetrical=False, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-published"]
        get_latest_by = "-published"


class Member(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(max_length=5000)
    title = models.CharField(max_length=255)
    currentResearch = models.TextField(max_length=5000)
    short_description = models.TextField(max_length=1000)

    publications = models.ManyToManyField(Publication,
                                          symmetrical=False, blank=True)

    def __str__(self):
        return self.name


class Seminar(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    title = models.CharField(max_length=400)
    time_and_place = models.CharField(max_length=400)
    description = models.TextField(max_length=5000)

    def __str__(self):
        return self.title

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("start date > end date")

    class Meta:
        ordering = ["-start_date", "end_date"]
        get_latest_by = "-start_date"


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
