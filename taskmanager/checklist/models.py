# ------------------------------------------------------------
# НЕОБХОДИМО ПЕРЕСМОТРЕТЬ ПОВЕДЕНИЕ on_delete для всех моделей
# ------------------------------------------------------------


from django.db import models
from django.contrib.auth.models import User

"""
Добавить класс для разграничения доступа
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Связь один к одному с моделью User
    is_privileged = models.BooleanField(default=False)  # Дополнительное поле для определения прав

    def __str__(self):
        return f"Профиль для {self.user.username}"
"""


class Department(models.Model):

    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)


class Task(models.Model):

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    check_list = models.ForeignKey("CheckList", on_delete=models.CASCADE, related_name='tasks')
    order = models.PositiveIntegerField(default=0)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    requires_photo = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class TaskPhoto(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='example_photos')
    photo = models.ImageField(upload_to='task_examples/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото примера выполнения для {self.task.title}"


class CheckList(models.Model):

    title = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_checklists', null=True, blank=True
    )

    def __str__(self):
        return self.title


class CheckListAssignment(models.Model):

    checklist = models.ForeignKey(CheckList, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_checklists')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Назначение {self.checklist} для {self.assigned_to}"


class CheckListExecution(models.Model):

    checklist = models.ForeignKey(CheckList, on_delete=models.CASCADE, related_name='executions')
    executed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='executed_checklists')
    start_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
    ], default='in_progress')

    def __str__(self):
        return f"Исполнение {self.checklist} пользователем {self.executed_by}"


class TaskExecutions(models.Model):

    execution = models.ForeignKey(CheckListExecution, on_delete=models.CASCADE, related_name='item_executions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_tasks')
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"Выполнение задачи {self.task} в рамках {self.execution}"


class TaskExecutionPhoto(models.Model):

    task_execution = models.ForeignKey(TaskExecutions, on_delete=models.CASCADE, related_name='result_photos')
    photo = models.ImageField(upload_to='task_results/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото результата для {self.task_execution.task.title}"
