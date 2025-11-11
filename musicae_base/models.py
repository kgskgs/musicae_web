from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField  # or TextField if you prefer

class UrlItem(models.Model):
    text = models.CharField(max_length=255)
    target = models.CharField(max_length=255, unique=True)
    children = models.ManyToManyField("self",
                                      symmetrical=False, blank=True)

    position = models.IntegerField()
    showOnBar = models.BooleanField(default=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.text


    class Meta:
        verbose_name = "Research Theme"
        verbose_name_plural = "Research Themes"
        ordering = []

    def __str__(self):
        return self.title or str(self.link.text)


class Contact(models.Model):
    time = models.DateTimeField(auto_now_add=True)
