from rest_framework import serializers

from .models import Monitor

class MonitorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Monitor

        fields = [
            "id",
            "name",
            "url",
            "interval_seconds",
            "is_active",
            "current_status",
            "created_at",
            "updated_at",
        ]