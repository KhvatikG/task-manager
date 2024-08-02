# ------------------------------------------------------------
# TODO: ПЕРЕСМОТРЕТЬ ПОВЕДЕНИЕ on_delete для всех моделей
# TODO: Добавить индексы
# ------------------------------------------------------------


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class Role(models.Model):

    role_name = models.CharField(max_length=30)
    can_create_update = models.BooleanField(default=False)
    users = models.ManyToManyField(User, related_name='roles', blank=True, null=True)

    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='created_roles', null=True, blank=True
    )
    update_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='updated_roles', null=True, blank=True
    )

    def __str__(self):
        return f"Роль: {self.role_name}"


class Department(models.Model):

    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Отдел: {self.name}"


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


class TaskExamplePhoto(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='example_photos')
    photo = models.ImageField(upload_to='task_examples/')
    description = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

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
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignment',
        null=True,
        blank=True,
    )
    group_assigned = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='assignment',
        null=True,
        blank=True,
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('checklist', 'group_assigned'),)

    def clean(self):
        if self.assigned_to and self.group_assigned:
            raise ValidationError(
                "Можно заполнить только одно поле: assigned_to или group_assigned."
            )
        if not self.assigned_to and not self.group_assigned:
            raise ValidationError(
                "Необходимо заполнить хотя бы одно поле: assigned_to или group_assigned."
            )
        return super().clean()

    def __str__(self):
        return f"Назначение {self.checklist} для user: {self.assigned_to}, group: {self.group_assigned}"


class CheckListExecution(models.Model):

    checklist = models.ForeignKey(CheckList, on_delete=models.CASCADE, related_name='executions')
    executed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='executed_checklists')
    start_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
    ], default='in_progress')

    # Поле для даты без времени, для отслеживания уникальности(один уникальный чек-лист в один день)
    start_date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = (('checklist', 'start_date'),)

    def __str__(self):
        return f"Исполнение {self.checklist} пользователем {self.executed_by}"


class TaskExecutions(models.Model):

    execution = models.ForeignKey(CheckListExecution, on_delete=models.CASCADE, related_name='item_executions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_tasks')
    comments = models.TextField(blank=True)

    # Поле для даты без времени, для отслеживания уникальности(одна уникальная таска в один день)
    completed_date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = (('task', 'completed_date'),)

    def __str__(self):
        return f"Выполнение задачи {self.task} в рамках {self.execution}"


class TaskExecutionPhoto(models.Model):

    task_execution = models.ForeignKey(TaskExecutions, on_delete=models.CASCADE, related_name='result_photos')
    photo = models.ImageField(upload_to='task_results/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото результата для {self.task_execution.task.title}"
