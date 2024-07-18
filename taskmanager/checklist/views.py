from rest_framework import generics

from checklist.models import Task, Department, CheckList
from checklist.serializers import TaskSerializer, DepartmentSerializer, CheckListSerializer


class TaskAPIList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskAPIUpdate(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class DepartmentAPIList(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentAPIUpdate(generics.UpdateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CheckListAPIList(generics.ListCreateAPIView):
    queryset = CheckList.objects.all()
    serializer_class = CheckListSerializer


class CheckListAPIUpdate(generics.UpdateAPIView):
    queryset = CheckList.objects.all()
    serializer_class = CheckListSerializer
