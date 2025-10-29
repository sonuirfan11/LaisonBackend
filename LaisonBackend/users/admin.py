from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("id", "mobile", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("mobile", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("mobile", "password1", "password2", "is_staff", "is_active")}
         ),
    )

    search_fields = ("mobile",)
    ordering = ("-id",)
