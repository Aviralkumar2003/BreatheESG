from rest_framework import serializers
from .models import IngestionJob

class IngestionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionJob
        fields = '__all__'
