from django.contrib import admin

# Register your models here.
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')
admin.site.register(CustomUser, CustomUserAdmin)