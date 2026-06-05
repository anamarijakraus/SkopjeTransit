from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_driver', 'is_passenger', 'is_staff', 'date_joined']
    list_filter = ['is_driver', 'is_passenger', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Ride Role', {'fields': ('is_driver', 'is_passenger')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Ride Role', {'fields': ('is_driver', 'is_passenger')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']
