import ast
import json

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from checklist.models import Task, Department, CheckList, TaskExamplePhoto
from checklist.serializers import (
    TaskSerializer,
    DepartmentSerializer,
    CheckListSerializer,
    TaskExamplePhotoSerializer,
)

# Вьюшка для получения/добавления пользователей
"""
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Ограничиваем доступ только для администраторов
"""


class TaskAPIView(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    parser_classes = [MultiPartParser, FormParser]

    # permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        # Создаём сериализатор для таски
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Сохраняем таску
        task = serializer.save()

        # Извлекаем список фотографий из запроса и данные для FotoExample и объедением.
        photos = self.parse_photo_example_objects(request.data, task.id)

        # Добавляем фото сериализатор, валидируем и сохраняем
        photo_serializer = TaskExamplePhotoSerializer(data=photos, many=True)
        photo_serializer.is_valid(raise_exception=True)
        photo_serializer.save()

        return Response(serializer.data)


    @transaction.atomic
    def update(self, request, *args, **kwargs):
        # ---------------------------------------------------------------
        print(request.headers)
        print(f"Во вьюхе: \n {request.data}")
        print(f"Фото: \n {request.data.getlist('photo')}")
        p: InMemoryUploadedFile = request.data.getlist('photo')[0]
        print(p.name)

        # ----------------------------------------------------------------
        partial = kwargs.pop('partial', False)

        # Создаём сериализатор для таски
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Сохраняем таску
        task = serializer.save()

        # Извлекаем список фотографий из запроса и данные для FotoExample и объедением.
        photos = self.parse_photo_example_objects(request.data, task.id)
        print(f"Photos: {photos}")

        for photo in photos:
            # Если есть поле id, то изменяем существующую модель фото примера
            if photo_id := photo.get('id', False):
                photo_instance = TaskExamplePhoto.objects.get(pk=photo_id)
                photo_serializer = TaskExamplePhotoSerializer(instance=photo_instance, data=photo, partial=True)
                photo_serializer.is_valid(raise_exception=True)
                photo_serializer.save()
            # Иначе создаём новую модель фото примера
            else:
                photo_serializer = TaskExamplePhotoSerializer(data=photo)
                photo_serializer.is_valid(raise_exception=True)
                photo_serializer.save()

        return Response(serializer.data)


    def parse_photo_example_objects(self, data, task_id):

        result = []

        photos_data = data.getlist('example_photos')
        photos = {photo.name: photo for photo in data.getlist('photo')}

        for photo_data in photos_data:
            photo_data_dict = ast.literal_eval(photo_data)
            photo_file_name = photo_data_dict.pop('file_name', False)

            if photo_file_name:
                photo_data_dict['photo'] = photos[photo_file_name]

            photo_data_dict['task'] = task_id
            result.append(photo_data_dict)

        return result

    @action(detail=True, methods=['DELETE'], url_path='remove-photo/(?P<photo_id>[^/.]+)')
    def remove_photo(self, request, pk=None, photo_id=None):
        task = self.get_object()
        photo = task.example_photos.filter(id=photo_id).first()

        if not photo:
            return Response(status=status.HTTP_404_NOT_FOUND)

        photo.photo.delete(save=False)  # Удаляем файл фото
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DepartmentAPIView(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckListAPIView(viewsets.ModelViewSet):
    queryset = CheckList.objects.all()
    serializer_class = CheckListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer: ModelSerializer):
        serializer.save(created_by=self.request.user)

    """
    Фильтрация
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'is_published']
    search_fields = ['title']
    ordering_fields = ['time_create', 'title']
    """

    # Метод для проверки прав доступа к методам вьюшки например Assignment
    """

    def get_permissions(self):
        /"/"/"
        В зависимости от метода (POST, PUT, DELETE) 
        устанавливаем разные разрешения.
        /"/"/"
        if self.request.method in permissions.SAFE_METHODS:
            # Для GET, HEAD, OPTIONS разрешаем всем аутентифицированным пользователям
            return [permissions.IsAuthenticated()]
        else:
            # Для POST, PUT, DELETE требуем права "create_checklistassignment"
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
    
    *  В  permission_classes  мы  указываем,  что  доступ  к  CheckListAssignmentViewSet  имеют  только  авторизованные  пользователи.
    *  get_permissions  переопределяет  метод,  который  устанавливает  разные  permissions  в  зависимости  от  метода  HTTP-запроса.
    *  В  get_permissions  мы  проверяем,  является  ли  метод  SAFE_METHODS  (GET, HEAD, OPTIONS),  и  если  да,  то  разрешаем  доступ  всем  авторизованным  пользователям.  
    *  Для  POST,  PUT,  DELETE  методов  мы  требуем  права  IsAdminUser,  чтобы  только  администраторы  могли  создавать,  изменять  и  удалять  назначения.
    """
