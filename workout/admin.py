from django.contrib import admin

from .models import Movement


class MovementAdmin(admin.ModelAdmin):
    list_display = ('name', 'modality', 'type', 'body_part', 'equipment')
    list_filter = ('modality', 'type', 'body_part', 'equipment')
    search_fields = ('name', 'description')


admin.site.register(Movement, MovementAdmin)
