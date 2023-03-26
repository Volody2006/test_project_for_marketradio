from django.db import models
from django.conf import settings
from django.urls import reverse


class CompositionAbstact(models.Model):
    title = models.CharField(
        verbose_name="Название", max_length=200, blank=True, null=True
    )
    artist = models.CharField(
        verbose_name="Исполнитель", max_length=200, blank=True, null=True
    )
    genre = models.CharField(verbose_name="Жанр", max_length=200, blank=True,
                             null=True)
    style = models.CharField(
        verbose_name="Стиль", max_length=200, blank=True, null=True
    )
    lyrics = models.TextField(verbose_name="Текст песни", blank=True,
                              null=True)
    release_date = models.DateField(verbose_name="Дата релиза", blank=True,
                                    null=True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class CompositionDiscogs(CompositionAbstact):
    release = models.IntegerField(verbose_name="Release ID")


class CompositionGenius(CompositionAbstact):
    release = models.IntegerField(verbose_name="Release ID")


class CompositionAudd(CompositionAbstact):
    class Meta:
        abstract = False


class SearchName(models.Model):
    file_name = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(
        verbose_name="Файл для поиска в audd.io",
    )
    discogs = models.ForeignKey(
        CompositionDiscogs, on_delete=models.SET_NULL, blank=True, null=True
    )
    genius = models.ForeignKey(
        CompositionGenius, on_delete=models.SET_NULL, blank=True, null=True
    )
    audd = models.ForeignKey(
        CompositionAudd, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        if self.file:
            return self.file.name
        return f"Search Name {self.pk}"

    def save(self, *args, **kwargs):
        if not self.pk:
            # file is being saved for the first time
            self.file.name = '{}'.format(self.file.name)
        super().save(*args, **kwargs)

    def get_file_url(self):
        if self.file:
            absolute_url = 'https://' + settings.NGROK_DOMAIN + self.file.url
            return absolute_url
        return ""

    def get_absolute_url(self):
        return reverse('demo:detail', kwargs={'pk': self.pk})