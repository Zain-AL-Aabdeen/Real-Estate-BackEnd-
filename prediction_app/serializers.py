from rest_framework import serializers
from .models import History

class HistorySerializer(serializers.ModelSerializer):
    # إجبار الحقل على العمل كـ JSONField صريح في الـ API
    Services = serializers.JSONField(required=False)

    class Meta:
        model = History
        fields = '__all__'
        read_only_fields = ['id', 'user', 'price']