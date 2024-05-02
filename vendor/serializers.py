from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Vendor



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {"password": {"write_only":True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    


class VendorSerializer(serializers.ModelSerializer): # for post and put
   
    class Meta:
        model = Vendor
        fields = '__all__'


class VendorReadOnlySerializer(serializers.ModelSerializer): # uses only for read only(get method).. reduces complexity
    user = UserSerializer()
    class Meta:
        model = Vendor
        fields = '__all__'