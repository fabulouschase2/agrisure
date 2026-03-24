from rest_framework import serializers
from .models import Farmer

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['username', 'password', 'phone', 'location', 'farm_size']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = Farmer.objects.create_user(**validated_data)
        return user