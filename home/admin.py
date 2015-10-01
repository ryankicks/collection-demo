from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from home.models import Collection 

# Register your models here.

UserAdmin.list_display = ('first_name', 'last_name', 'email', 'date_joined', 'is_active', 'is_staff', 'is_superuser')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ['created_time']

admin.site.register(Collection, CollectionAdmin)

