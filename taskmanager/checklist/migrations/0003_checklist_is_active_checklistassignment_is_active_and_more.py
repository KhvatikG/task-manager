# Generated by Django 5.0.6 on 2024-07-23 11:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0002_checklist_created_by_task_order_task_requires_photo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklist',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='checklistassignment',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='task',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='TaskExamplePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='task_examples/')),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='example_photos', to='checklist.task')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.DeleteModel(
            name='TaskPhoto',
        ),
    ]
