from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


# -------------------------
# 1. WISHLIST
# -------------------------
class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE,
        related_name="items"
    )
    service = models.ForeignKey(
        "services.Service",  # points to your Service table
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wishlist", "service")

    def __str__(self):
        return f"{self.service.title}"


# -------------------------
# 2. CART SESSION
# -------------------------
class CartSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="carts"
    )
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user}" if self.user else f"Guest Cart {self.session_id}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        CartSession, on_delete=models.CASCADE,
        related_name="items"
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "service")

    def __str__(self):
        return f"{self.quantity} x {self.service.title}"


# -------------------------
# 3. COUPONS / PROMO CODES
# -------------------------
class Coupon(models.Model):

    DISCOUNT_TYPE_CHOICES = [
        ("PERCENT", "Percentage"),
        ("FLAT", "Flat Amount"),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    discount_type = models.CharField(
        max_length=10, choices=DISCOUNT_TYPE_CHOICES
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    max_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # For percentage caps

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(default=1)  # global usage
    per_user_limit = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date
        )

    def __str__(self):
        return self.code


# -------------------------
# 4. CLIENT COUPON (REDEMPTION TRACKER)
# -------------------------
class ClientCoupon(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_coupons"
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="coupon_usage"
    )
    times_used = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "coupon")

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"
