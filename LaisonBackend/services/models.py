from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from users.models import BaseModel, ProfessionalProfile
from django.utils import timezone
from django.conf import settings


class Category(MPTTModel, BaseModel):
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    icon = models.URLField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Service(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services")
    title = models.CharField(max_length=150)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()  # e.g., 60 mins
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ServiceSpecification(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="specifications")
    title = models.CharField(max_length=200)  # e.g., "Includes chemical cleaning"
    value = models.CharField(max_length=200)  # e.g., "Yes" or "2 cleaners"
    unit = models.CharField(max_length=50, null=True, blank=True)  # optional
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.service.title} - {self.title}"


class ServiceAddon(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="addons")
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=255, null=True, blank=True)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.service.title} - Addon: {self.name}"


class ServiceMedia(models.Model):
    MEDIA_TYPE = (
        ("image", "Image"),
        ("video", "Video"),
    )

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE)
    file_url = models.URLField(max_length=300)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.service.title} - {self.media_type}"


class ProfessionalService(models.Model):
    professional = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="services"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="professionals"
    )
    custom_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )  # optional if professional charges differently
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("professional", "service")

    def __str__(self):
        return f"{self.professional.user.full_name} - {self.service.title}"


class ServiceReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_reviews"
    )

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    service_request = models.ForeignKey(
        "orders.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="service_reviews"
    )

    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField(blank=True)

    # Media uploaded with review
    images = models.JSONField(null=True, blank=True)  # list of URLs
    videos = models.JSONField(null=True, blank=True)

    is_verified = models.BooleanField(default=True)  # only after completed order
    is_visible = models.BooleanField(default=True)   # admin moderation

    helpful_count = models.PositiveIntegerField(default=0)
    reported_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} - {self.rating}★"


class ProfessionalReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professional_reviews"
    )

    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received"
    )

    service_request = models.ForeignKey(
        "orders.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="professional_reviews"
    )

    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField(blank=True)

    # Media support
    images = models.JSONField(null=True, blank=True)
    videos = models.JSONField(null=True, blank=True)

    # For professional response
    reply_text = models.TextField(blank=True)
    reply_at = models.DateTimeField(null=True, blank=True)

    is_verified = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)

    helpful_count = models.PositiveIntegerField(default=0)
    reported_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pro {self.professional_id} - {self.rating}★"
