from django.conf import settings
from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class ArchivableModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def archive(self):
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save(update_fields=["is_archived", "archived_at", "updated_at"])

    def restore(self):
        self.is_archived = False
        self.archived_at = None
        self.save(update_fields=["is_archived", "archived_at", "updated_at"])


class Include(ArchivableModel):
    description = models.TextField("Описание")
    icon_path = models.CharField("Иконка (путь в media)", max_length=500, blank=True)

    class Meta:
        verbose_name = "Include"
        verbose_name_plural = "Includes"
        ordering = ["description"]

    def __str__(self):
        return self.description[:80]

    @property
    def icon_url(self):
        if not self.icon_path:
            return ""
        return f"{settings.MEDIA_URL}{self.icon_path}"


class Attraction(ArchivableModel):
    title = models.CharField("Заголовок", max_length=255)
    description = models.TextField("Описание")
    city = models.CharField("Город", max_length=120)
    address = models.CharField("Адрес", max_length=255)
    duration_hours = models.DecimalField("Длительность, часов", max_digits=5, decimal_places=2)
    photo = models.ImageField("Фотография", upload_to="catalog/attractions/photos/", null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_attractions",
        verbose_name="Создатель",
    )

    class Meta:
        verbose_name = "Достопримечательность"
        verbose_name_plural = "Достопримечательности"
        ordering = ["title"]

    def __str__(self):
        return self.title


class ToursDay(ArchivableModel):
    title = models.CharField("Заголовок", max_length=255)
    description = models.TextField("Описание")
    city = models.CharField("Город", max_length=120)
    address = models.CharField("Адрес", max_length=255)
    duration_hours = models.DecimalField("Длительность, часов", max_digits=5, decimal_places=2)
    photo = models.ImageField("Фотография", upload_to="catalog/tours_days/photos/", null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tours_days",
        verbose_name="Создатель",
    )
    attractions = models.ManyToManyField(
        Attraction,
        through="ToursDayAttraction",
        related_name="tours_days",
        verbose_name="Достопримечательности",
        blank=True,
    )
    includes = models.ManyToManyField(
        Include,
        through="ToursDayInclude",
        related_name="tours_days",
        verbose_name="Includes",
        blank=True,
    )

    class Meta:
        verbose_name = "ToursDay"
        verbose_name_plural = "ToursDays"
        ordering = ["title"]

    def __str__(self):
        return self.title


class ToursDayAttraction(models.Model):
    tours_day = models.ForeignKey(ToursDay, on_delete=models.CASCADE)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("tours_day", "attraction")
        ordering = ["position", "id"]
        verbose_name = "Связь ToursDay -> Достопримечательность"
        verbose_name_plural = "Связи ToursDay -> Достопримечательность"

    def __str__(self):
        return f"{self.tours_day} -> {self.attraction}"


class ToursDayInclude(models.Model):
    tours_day = models.ForeignKey(ToursDay, on_delete=models.CASCADE)
    include = models.ForeignKey(Include, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("tours_day", "include")
        ordering = ["position", "id"]
        verbose_name = "Связь ToursDay -> Include"
        verbose_name_plural = "Связи ToursDay -> Include"

    def __str__(self):
        return f"{self.tours_day} -> {self.include}"


class GroupTour(ArchivableModel):
    title = models.CharField("Заголовок", max_length=255)
    short_description = models.CharField("Краткое описание", max_length=255)
    description = models.TextField("Описание")
    group_size = models.PositiveIntegerField("Численность группы")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_group_tours",
        verbose_name="Создатель",
    )
    tour_days = models.ManyToManyField(
        ToursDay,
        through="GroupTourDay",
        related_name="group_tours",
        verbose_name="Дни тура",
        blank=True,
    )

    class Meta:
        verbose_name = "GroupTour"
        verbose_name_plural = "GroupTours"
        ordering = ["title"]

    def __str__(self):
        return self.title


class GroupTourDay(models.Model):
    group_tour = models.ForeignKey(GroupTour, on_delete=models.CASCADE)
    tours_day = models.ForeignKey(ToursDay, on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("group_tour", "tours_day")
        ordering = ["day_number", "id"]
        verbose_name = "Связь GroupTour -> ToursDay"
        verbose_name_plural = "Связи GroupTour -> ToursDay"

    def __str__(self):
        return f"{self.group_tour} / day {self.day_number}: {self.tours_day}"


class GroupTourMedia(models.Model):
    IMAGE = "image"
    VIDEO = "video"
    MEDIA_TYPE_CHOICES = (
        (IMAGE, "Фото"),
        (VIDEO, "Видео"),
    )

    group_tour = models.ForeignKey(GroupTour, on_delete=models.CASCADE, related_name="media_items")
    file = models.FileField("Файл", upload_to="catalog/group_tours/media/")
    media_type = models.CharField("Тип медиа", max_length=10, choices=MEDIA_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Медиа GroupTour"
        verbose_name_plural = "Медиа GroupTour"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.group_tour}: {self.media_type}"


class BlogPost(ArchivableModel):
    """Blog post: image, date, title, body (full article on separate page)."""
    title = models.CharField("Title", max_length=255)
    body = models.TextField("Body")
    published_at = models.DateField("Publication date", null=True, blank=True)
    image = models.ImageField(
        "Image",
        upload_to="catalog/blog/images/",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_blog_posts",
        verbose_name="Author",
    )

    class Meta:
        verbose_name = "Blog post"
        verbose_name_plural = "Blog"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title[:80]
