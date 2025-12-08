from django.db import models
from django.conf import settings
from django.utils import timezone


# Create your models here.

#SERvice Request (Orders)
class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted by Professional"),
        ("ASSIGNED", "Professional Assigned"),
        ("IN_PROGRESS", "Work In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("REFUNDED", "Refunded"),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_requests"
    )

    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_requests"
    )

    address = models.ForeignKey(
        "users.ClientAddress",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    coupon = models.ForeignKey(
        "commerce.Coupon",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default="PENDING"
    )

    requested_datetime = models.DateTimeField()  # When client wants service
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.client}"


# ------------------------------------------
# SERVICE REQUEST ITEMS
# ------------------------------------------
class ServiceRequestItem(models.Model):
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="items"
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    addons_selected = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.service.title} (Order {self.service_request.id})"


# ------------------------------------------
# SERVICE REQUEST STATUS HISTORY
# ------------------------------------------
class ServiceRequestStatusHistory(models.Model):
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="status_history"
    )
    status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True

    )

    def __str__(self):
        return f"{self.service_request.id} → {self.status}"
