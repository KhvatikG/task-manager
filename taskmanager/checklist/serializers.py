from rest_framework import serializers

from django.contrib.auth.models import User

from .models import (
    Task,
    Department,
    CheckList,
    TaskExamplePhoto,
    CheckListAssignment,
    CheckListExecution,
    TaskExecutions,
    TaskExecutionPhoto
    )
# Модель включающая userprofile для расширения полей, для начала реализует разграничение прав
"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff', 'is_active', 'userprofile']  # укажите поля, которые должны быть представлены

    def create(self, validated_data):
        # Извлечем UserProfile, если он есть
        user_profile_data = validated_data.pop('userprofile', None)
        
        # Создаем нового пользователя
        user = User(*validated_data)
        user.set_password(validated_data['password'])  # Храните пароль в зашифрованном виде
        user.save()
        
        # Создаем UserProfile, если он есть
        if user_profile_data:
            UserProfile.objects.create(user=user, *user_profile_data)

        return user
"""


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description"]


class TaskPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExamplePhoto
        fields = ["id", "photo", "description", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]

    def validate_photo(self, value):
        if not value.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError("Неподдерживаемый формат фото.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    example_photos = TaskPhotoSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "check_list",
            "order",
            "requires_photo",
            "example_photos",
            "time_create",
            "time_update",
        ]
        read_only_fields = [
            "id",
            "time_create",
            "time_update",
        ]


class CheckListSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = CheckList
        fields = [
            "id",
            "title",
            "department",
            "time_create",
            "time_update",
            "is_published",
            "tasks",
            "created_by",
        ]
        read_only_fields = [
            "id",
            "time_create",
            "time_update",
            "created_by",
        ]


class CheckListsAssignmentSerializer(serializers.ModelSerializer):
    checklist = CheckListSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = CheckListAssignment
        fields = [
            "id",
            "checklist",
            "assigned_to",
            "assigned_at"
        ]
        read_only_fields = [
            "id",
            "assigned_at",
        ]


class TaskExecutionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExecutionPhoto
        fields = [
            "id",
            "task_execution",
            "photo",
            "uploaded_at"
        ]
        read_only_fields = [
            "id",
            "uploaded_at",
        ]


class TaskExecutionSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    completed_by = UserSerializer(read_only=True)
    result_photos = TaskExecutionPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = TaskExecutions
        fields = [
            "id",
            "execution",
            "task",
            "is_done",
            "completed_at",
            "completed_by",
            "comments",
            "result_photos",
        ]
        read_only_fields = [
            "id",
            "completed_at",
            "completed_by",
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['completed_by'] = user
        return super().create(validated_data)


class CheckListExecutionSerializer(serializers.ModelSerializer):
    checklist = CheckListSerializer(read_only=True)
    executed_by = UserSerializer(read_only=True)
    item_executions = TaskExecutionSerializer(many=True, read_only=True)

    class Meta:
        model = CheckListExecution
        fields = [
            "id",
            "checklist",
            "executed_by",
            "start_at",
            "completed_at",
            "status",
            "item_executions"
        ]
        read_only_fields = [
            "id",
            "executed_by",
            "start_at"
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['executed_by'] = user
        return super().create(validated_data)
