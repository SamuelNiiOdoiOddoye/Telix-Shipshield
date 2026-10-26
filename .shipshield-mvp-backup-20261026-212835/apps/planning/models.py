import uuid

from django.conf import settings 
from django.db import models

class Milestone(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta :
        ordering = ["order","created_at"]
        
    def __str__(self):
        return self.title
    
class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo","To do"
        IN_PROGRESS = "in_progresss" ,"In progress"
        BLOCKED = "blocked","Blocked"
        DONE = "done","Done"
        
    class Priority(models.TextChoices):
        LOW = "low","Low"
        MEDIUM = "medium","Medium"
        HIGH = "high","High"
        CRITICAL = "critical","Critical"
        
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.CASCADE,
        related_name = "tasks",
        null = True,
        blank = True,
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default= Status.TODO,
    )
    
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        
    )
    
    order = models.PositiveIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order","-created_at"]
        
    def __str__(self):
        return self.title
    
class AcceptanceCriterion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name = "acceptance_criteria"
    )   
    
    description = models.CharField(max_length=500)
    is_met = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["created_at"]
        
    def __str__(self):
        return self.description
    


class ProjectPlan(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"

    project = models.OneToOneField(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="plan_draft",
    )
    plan = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_shipshield_plans",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Plan for {self.project.name} ({self.status})"
