from django.contrib import admin

from .models import Movement, WorkoutComponent, Workout, Score


class MovementAdmin(admin.ModelAdmin):
    list_display = ('name', 'modality', 'type', 'body_part', 'equipment')
    list_filter = ('modality', 'type', 'body_part', 'equipment')
    search_fields = ('name', 'description')


admin.site.register(Movement, MovementAdmin)


class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'total_reps', 'time_cap', 'is_active', 'is_scaled')
    list_filter = ('name', 'type', 'is_active', 'is_scaled')
    search_fields = ('name', 'description')


admin.site.register(Workout, WorkoutAdmin)


class WorkoutComponentAdmin(admin.ModelAdmin):
    list_display = ('workout', 'movement', 'reps', 'sequence')
    list_filter = ('workout', 'movement', 'reps', 'sequence')
    search_fields = ('workout', 'movement')


admin.site.register(WorkoutComponent, WorkoutComponentAdmin)


class ScoreAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'workout', 'score')
    list_filter = ('athlete', 'workout')
    search_fields = ('athlete', 'workout', 'competition')


admin.site.register(Score, ScoreAdmin)
