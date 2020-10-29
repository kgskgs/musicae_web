from django.db import models


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


class Page(models.Model):
    link = models.OneToOneField(
        UrlItem,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='page_for',
    )
    content = models.TextField()

    keywords = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.link.text
