from django.db import models
from django.utils.translation import gettext_lazy as _


class pTopic(models.Model):
    text = models.CharField(max_length=250)

    def __str__(self):
        return self.text


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

    fname = models.CharField(max_length=255, blank=True)

    topics = models.ManyToManyField(pTopic,
                                    symmetrical=False, blank=True)

    def __str__(self):
        return self.title


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
