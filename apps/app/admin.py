from django.contrib import admin
from . import models
# Register your models here.


admin.site.site_header = 'ALIE API'
admin.site.site_title = 'ALIE API'
admin.site.index_title = 'ALIE API'


@admin.register(models.Human)
class HumanAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'dni',
        'birth_date',
        'cover_dni',
        'back_cover_dni',
        'photo'
    ]

