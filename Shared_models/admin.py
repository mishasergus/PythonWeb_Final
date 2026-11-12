from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Application_category, Application, Comment


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Додаємо поле role до стандартного виведення користувачів Django Admin
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Роль користувача", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Роль користувача", {"fields": ("role",)}),
    )


@admin.register(Application_category)
class ApplicationCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("created_at", "creator")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "priority",
        "status",
        "creator",
        "performer",
        "created_at",
    )
    list_filter = ("status", "priority", "category", "created_at")
    search_fields = ("name", "description", "creator__username", "performer__username")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CommentInline]  # Дозволяє бачити та керувати коментарями прямо всередині заявки


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "creator", "is_viewable", "created_at")
    list_filter = ("is_viewable", "created_at")
    search_fields = ("text", "creator__username", "application__name")
    readonly_fields = ("created_at",)