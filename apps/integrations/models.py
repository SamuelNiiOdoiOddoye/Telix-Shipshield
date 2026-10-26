import uuid

from django.conf import settings
from django.db import models

class Repository(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="repositories",
    )
    
    provider = models.CharField(max_length=30, default="github")
    repository_url = models.URLField(max_length=500)
    owner_name = models.CharField(max_length=500)
    repository_name = models.CharField(max_length=200, blank=True)
    default_branch = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    connected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connected_repositories",
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-updated_at"]
        
    def __str__(self):
        return self.repository_name or self.repository_url
    
class AuditRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending","Pending"
        RUNNING = "running","Running"
        COMPLETED = "completed","Completed"
        FAILED = "failed","Failed"
        
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    repository = models.ForeignKey(
        Repository,
        on_delete = models.CASCADE,
        related_name = "audit_runs"
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    
    summary = models.TextField(blank=True)
    findings = models.JSONField(default=list, blank=True)
    commit_sha = models.CharField(max_length=64, blank=True)
    started_at = models.DateTimeField(null=True,blank=True)
    completed_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"Audit of {self.repository} ({self.status})"
    
    
class ReadinessReport(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft ", "Draft"
        READY = "ready", "Ready"
        NEEDS_WORK = "needs_work", "Needs work"
        BLOCKED = "blocked", "Blocked"
        
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="readiness_reports",
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    
    score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    
    summary = models.TextField(blank=True)
    findings = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list,blank=True)
    
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        blank=True, 
        null=True,
        related_name = "generated_readiness_reports",
    )
        
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"Readiness report for {self.project}"