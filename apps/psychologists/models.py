from django.db import models

class Psychologist(models.Model):

    SPECIALIZATION_CHOICES = [
        ('ANXIETY', 'Anxiety'),
        ('DEPRESSION', 'Depression'),
        ('STRESS', 'Stress Management'),
        ('CAREER', 'Career Counselling'),
        ('RELATIONSHIP', 'Relationship Counselling'),
        ('GENERAL', 'General Counselling'),
    ]

    full_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)

    specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES
    )

    experience_years = models.PositiveIntegerField()

    bio = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.specialization})"