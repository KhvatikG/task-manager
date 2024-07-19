from rest_framework import generics, viewsets, permissions
from rest_framework.serializers import ModelSerializer

from checklist.models import Task, Department, CheckList
from checklist.serializers import TaskSerializer, DepartmentSerializer, CheckListSerializer


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
