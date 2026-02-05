from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from accounts.models import SoftDeleteModel


class WorkStream(SoftDeleteModel):
    """
    Workstream managed by a manager.
    Schema: Work_streams table
    """
    workstream_name = models.CharField(max_length=255, help_text="Workstream name")
    description = models.TextField(null=True, blank=True, help_text="Workstream description")
    manager = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_workstreams",
        help_text="Manager of this workstream"
    )
    capacity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of schools"
    )
    location = models.CharField(max_length=255, null=True, blank=True, help_text="Workstream regional location")
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="Workstream URL slug")
    
    def save(self, *args, **kwargs):
        if not self.slug or self.slug.strip() == "":
            # Create a unique slug
            base_slug = slugify(self.workstream_name)
            slug = base_slug
            counter = 1
            while WorkStream.all_objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = "work_streams"
        verbose_name = "Workstream"
        verbose_name_plural = "Workstreams"
        ordering = ["workstream_name"]
        indexes = [
            models.Index(fields=["manager"], name="idx_work_streams_manager"),
        ]
    
    def __str__(self):
        return self.workstream_name

