from rest_framework import viewsets, permissions
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
    permission_classes = [permissions.IsAuthenticated]


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