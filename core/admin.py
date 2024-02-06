from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.forms import CustomUserCreationForm, CustomUserChangeForm
from core.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'user_image', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_image',)}),
    )


