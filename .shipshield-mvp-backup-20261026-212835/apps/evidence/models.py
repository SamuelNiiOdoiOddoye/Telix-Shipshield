import uuid 

from django.conf import settings
from django.db import models

class Evidence(models.Model):
    class EvidenceType(models.TextChoices):
        LINK = "link", "Link",
        FILE = "file", "File",
        NOTE = "note", "Note",
        SCREENSHOT = "screenshot" , "Screenshot"
        OTHER = "other", "Other",
        
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    task = models.ForeignKey(
        "planning.Task",
        on_delete = models.CASCADE,
        related_name = "evidence",
    )
    
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_evidence"
    )
    
    evidence_type = models.CharField(
        max_length=20,
        choices= EvidenceType.choices,
        default=EvidenceType.NOTE,
    )
    
    title = models.CharField(
        max_length=20,
        choices=EvidenceType.choices,
        default=EvidenceType.NOTE,
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url= models.URLField(max_length=1000,blank=True)
    file = models.FileField(
        upload_to="evidence/%Y/%m/",
        blank=True,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta :
        ordering = ["-created_at"]
        
    def __str__(self):
        return self.title