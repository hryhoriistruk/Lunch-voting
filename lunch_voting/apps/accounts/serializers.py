from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Used by admins to provision a new employee account.

    Password is write-only and hashed via ``set_password`` in ``create``;
    the role is forced to EMPLOYEE regardless of what is posted, so this
    endpoint can never be used to accidentally mint another admin.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(role=User.Role.EMPLOYEE, **validated_data)
        user.set_password(password)
        user.save()
        return user


class EmployeeSerializer(serializers.ModelSerializer):
    """Read-only representation of an employee, e.g. for admin listings."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_active")
