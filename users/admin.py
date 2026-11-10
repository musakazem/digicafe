from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AdminProfile, User


class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'full_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'full_name']
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    inlines = [AdminProfileInline]
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('Profile', {'fields': ['full_name', 'role']}),
        ('Permissions', {'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']}),
        ('Dates', {'fields': ['last_login', 'created_at', 'updated_at']}),
    ]
    add_fieldsets = [
        (None, {'classes': ['wide'], 'fields': ['email', 'full_name', 'role', 'password1', 'password2']}),
    ]
