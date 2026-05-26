import uuid
from django.db import models
from ingestion.models import IngestionJob

class RawRecord(models.Model):
    STATUS_CHOICES = [
        ('OK', 'OK'),
        ('FAILED', 'Failed'),
        ('SUSPICIOUS', 'Suspicious'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(IngestionJob, on_delete=models.CASCADE, related_name='raw_records')
    raw_data = models.JSONField(default=dict)
    parse_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OK')
    parse_error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"RawRecord {self.id} - {self.parse_status}"

class NormalizedRecord(models.Model):
    SCOPE_CHOICES = [
        ('SCOPE_1', 'Scope 1'),
        ('SCOPE_2', 'Scope 2'),
        ('SCOPE_3', 'Scope 3'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('FLAGGED', 'Flagged'),
        ('APPROVED', 'Approved'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raw_record = models.OneToOneField(RawRecord, on_delete=models.CASCADE, related_name='normalized_record')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    quantity_original = models.DecimalField(max_digits=19, decimal_places=4)
    unit_original = models.CharField(max_length=50)
    quantity_normalized = models.DecimalField(max_digits=19, decimal_places=4)
    unit_normalized = models.CharField(max_length=50)
    review_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    flag_note = models.TextField(blank=True, null=True)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            orig = NormalizedRecord.objects.get(pk=self.pk)
            if orig.is_locked:
                from django.core.exceptions import ValidationError
                raise ValidationError("Cannot modify an approved/locked record.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"NormRecord {self.id} - {self.scope}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('INGESTED', 'Ingested'),
        ('FLAGGED', 'Flagged'),
        ('EDITED', 'Edited'),
        ('APPROVED', 'Approved'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.CharField(max_length=255, default='system')
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"AuditLog {self.id} - {self.action}"
