from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Question, CustomUser,AmaliyotTuri


admin.site.register(Question)

@admin.register(AmaliyotTuri)
class AmaliyotTuriAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'slug')
    prepopulated_fields = {'slug': ('nomi',)}

# Register your models here.

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Qo‘shimcha ma’lumotlar', {
            'fields': ('date_of_birth', 'user_type', 'university', 'school'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)