from django.db import models
from django.conf import settings
from orders.models import ServiceRequest
import uuid


# Create your models here.
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("CARD", "Credit/Debit Card"),
        ("UPI", "UPI"),
        ("WALLET", "Wallet"),
        ("NET_BANKING", "Net Banking"),
        ("COD", "Cash on Delivery"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)

    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_gateway_response = models.JSONField(null=True, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} ({self.status})"


# ------------------------------------------
# 3. REFUND (TO CLIENT)
# ------------------------------------------
class Refund(models.Model):
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="refund"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()

    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    refund_transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    refund_gateway_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Refund for Payment {self.payment.transaction_id}"


# ------------------------------------------
# 4. PAYOUT (TO PROFESSIONAL)
# ------------------------------------------
class Payout(models.Model):
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payouts"
    )

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="payouts"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payout_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PROCESSING", "Processing"),
            ("SUCCESS", "Success"),
            ("FAILED", "Failed"),
        ],
        default="PENDING"
    )

    payout_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    payout_gateway_response = models.JSONField(null=True, blank=True)

    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payout {self.amount} to {self.professional}"


# ------------------------------------------
# 5. TRANSACTION LEDGER (OPTIONAL BUT RECOMMENDED)
# ------------------------------------------
class TransactionLedger(models.Model):
    ENTRY_TYPE = [
        ("DEBIT", "Debit"),
        ("CREDIT", "Credit"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    reference_id = models.CharField(max_length=255)  # payment_id / refund_id / payout_id
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entry_type} - {self.amount}"
