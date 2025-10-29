from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from .manager import CustomUserManager
from django.utils import timezone
import uuid
from datetime import timedelta, datetime


# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser, BaseModel, PermissionsMixin):
    username = None
    ROLE_CHOICES = [
        ("client", "Client"),
        ("professional", "Professional"),
        ("admin", "Admin"),
    ]
    mobile = PhoneNumberField(unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.mobile}"

    def set_otp(self, otp):
        self.otp = otp
        self.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.save(update_fields=["otp", "otp_expiry"])

    def is_otp_verified(self, otp):
        if self.otp == otp and self.otp_expiry > timezone.now():
            self.otp = None
            self.otp_expiry = None
            self.save(update_fields=["otp", "otp_expiry"])
            return True
        return False

    def get_full_name(self):
        return self.first_name + self.last_name


class ClientProfile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="client_profile")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Client Profile - {self.user.get_full_name}"


class ProfessionalProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="professional_profile")
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_verified = models.BooleanField(default=False)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Professional - {self.user.get_full_name}"


class ProfessionalVerification(models.Model):
    CRIMINAL_STATUS = [
        ("pending", "Pending"),
        ("clear", "Clear"),
        ("flagged", "Flagged"),
    ]

    professional = models.OneToOneField(
        ProfessionalProfile, on_delete=models.CASCADE, related_name="professional_verification"
    )
    id_proof_url = models.URLField(max_length=255, null=True, blank=True)
    skill_certificate_url = models.URLField(max_length=255, null=True, blank=True)
    criminal_check_status = models.CharField(
        max_length=20, choices=CRIMINAL_STATUS, default="pending"
    )
    verified_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_professionals"
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Verification - {self.professional.user.full_name}"
