from django.db import models


class UrlItem(models.Model):
    text = models.CharField(max_length=250)
    target = models.CharField(max_length=255, blank=True)
    children = models.ManyToManyField("self",
                                      symmetrical=False, blank=True)

    position = models.IntegerField()

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.text
