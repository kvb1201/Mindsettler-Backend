from rest_framework import serializers
from .models import Psychologist


class PsychologistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Psychologist
        fields = "__all__"