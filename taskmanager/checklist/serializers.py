from django.core.files.uploadedfile import InMemoryUploadedFile
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
    TaskExecutionPhoto,
    Role
)
# Модель включающая userprofile для расширения полей, для начала реализует разграничение прав.
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


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "id",
            "role_name",
            "can_create_update",
            "users",
            "time_create",
            "time_update",
            "created_by",
            "update_by"
        ]
        read_only_fields = ["id", "time_create", "time_update", "created_by", "updated_by"]


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "roles", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": False},
            "last_name": {"required": False}
        }

    def create(self, validated_data):
        """
        Ожидает роли в виде списка словарей по ключу roles
        "role_name": "имя существующей роли"
        """
        # Создаём объект пользователя
        user = User.objects.create_user(
            username=validated_data.pop("username", ""),
            password=validated_data.pop("password", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )

        # Извлекаем данные по ролям
        roles_data = validated_data.pop("roles")

        # Для каждой роли
        for role in roles_data:
            if role_name := role.get("role_name", False):  # Получаем имя роли, если есть
                role_instance = Role.objects.get(role_name=role_name)  # Получаем объект роли по имени
                role_instance.users.add(user.id)  # В поле пользователи полученной роли добавляем нового пользователя

        return validated_data


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description"]


class TaskExamplePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExamplePhoto
        fields = ["id", "task", "photo", "description", "uploaded_at", "order"]
        read_only_fields = ["id", "uploaded_at"]

    def validate(self, data):
        print(f"В фото сериализаторе {data}")
        return data

    def validate_photo(self, value):
        if not value.name.lower().endswith(('.jpg', '.jpeg')):
            raise serializers.ValidationError("Неподдерживаемый формат фото.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    example_photos = TaskExamplePhotoSerializer(many=True, required=False)

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

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance

    def validate_example_photos(self, data):
        return data

    def validate(self, data):
        print(f"В сериализаторе: \n {data}")
        if self.instance is None and 'check_list' not in data:
            raise serializers.ValidationError("check_list is required when creating a new Task")
        return data


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
    # checklist = CheckListSerializer(read_only=False)
    # assigned_to = UserSerializer(read_only=False, required=False)
    # group_assigned = RoleSerializer(read_only=False, required=False)

    class Meta:
        model = CheckListAssignment
        fields = [
            "id",
            "checklist",
            "assigned_to",
            "group_assigned",
            "assigned_at",
            "is_active"
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
