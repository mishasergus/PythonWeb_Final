from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        AGENT = 'agent', 'Agent'
        MANAGER = 'manager', 'Manager'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name="role"
    )

class Application_category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Category Name")

    def __str__(self):
        return self.name

class Application(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In_progress'
        WAITING_CLIENT = 'waiting_client', 'Waiting_client'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'
        REJECTED = 'rejected', 'Rejected'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Application Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    category = models.ForeignKey(
        Application_category,
        on_delete=models.PROTECT,
        related_name='applications',
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    finished_at = models.DateTimeField(null=True, verbose_name="Finished At")

    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='created_applications'
    )

    performer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='applications_to_do',
        null=True
    )



class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    is_viewable = models.BooleanField(default=True)
    text = models.TextField(blank=True, null=True, verbose_name="Text")
    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='comments'
    )




