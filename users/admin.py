from django.contrib import admin
from .models import Users
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class UsersAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'date_joined', 'last_login', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name', 'username')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Users, UsersAdmin)