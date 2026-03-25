from rest_framework import serializers
from .models import Farmer, Crop, FarmInput, LoanRequest

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['username', 'password', 'phone', 'location', 'farm_size']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Farmer.objects.create_user(**validated_data)
        return user

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = '__all__'

class FarmInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmInput
        fields = '__all__'

class LoanRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRequest
        fields = '__all__'