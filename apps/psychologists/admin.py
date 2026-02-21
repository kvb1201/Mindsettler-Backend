

# Register your models here.
from django.contrib import admin
from .models import Psychologist

@admin.register(Psychologist)
class PsychologistAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'specialization',
        'experience_years',
        'is_active',
    )
    list_filter = ('specialization', 'is_active')
    search_fields = ('full_name', 'email')