from rest_framework import serializers
from .models import Corporate


class CorporateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporate
        fields = "__all__"