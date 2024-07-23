from django.contrib import admin

from checklist.models import (
    CheckList,
    Task,
    Department,
    TaskExamplePhoto,
    CheckListAssignment,
    CheckListExecution,
    TaskExecutions,
    TaskExecutionPhoto,
)


admin.site.register([
    CheckList,
    Task,
    Department,
    TaskExamplePhoto,
    CheckListAssignment,
    CheckListExecution,
    TaskExecutions,
    TaskExecutionPhoto,
])
