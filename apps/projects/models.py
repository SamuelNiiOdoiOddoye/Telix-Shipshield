import uuid 

from django.conf import settings
from django.db import models

class Project(models.Model):
    class ProjectType(models.TextChoices):
        SOFTWARE = "software","Software"
        BUSINESS =  "business","Business"
        PERSONAL = "personal", "Personal"
        RESEARCH = "research","Research"
        OTHER = "other","Other"
        
    class Status(models.TextChoices):
        DRAFT ="draft","Draft"
        ACTIVE = "active","Active"
        ON_HOLD = "on_hold","On_hold"
        COMPLETED = "completed","Completed"
        ARCHIVED = "archived","Archived"
        
    id = models.UUIDField(
        primary_key  = True,
        default = uuid.uuid4,
        editable=False,
    )
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        related_name = "shipshield_projects",
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project_type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        default=ProjectType.OTHER,
    )
    
    status = models.CharField(
        max_length= 20,
        choices = Status.choices,
        default= Status.DRAFT,
    )
    
    goal = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta :
        ordering = ["-updated_at"]
        
    def __str__(self):
        return self.name