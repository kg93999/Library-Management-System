from rest_framework import serializers
from .models import MyUser, Books, BookIssued

from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import ValidationError

# from .utils import Util

class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = '__all__' 


class BookIssuedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookIssued
        fields = '__all__' 


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'  
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):     # Overriding... For more info read source code of serializers.ModelSerializer.create()
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length = 50, style = {'input_type':'password'}, write_only = True)
    password2 = serializers.CharField(max_length = 50, style = {'input_type':'password'}, write_only = True)
    class Meta:
        fields = ['password', 'password2']

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password & Confirm password does not match")
        user.set_password(password)
        user.save()
        return data
