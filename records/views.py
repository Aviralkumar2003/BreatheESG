from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import NormalizedRecord, AuditLog, RawRecord
from .serializers import NormalizedRecordSerializer, RawRecordSerializer

class RawRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RawRecord.objects.all().order_by('-job__ingested_at', 'id')
    serializer_class = RawRecordSerializer
    filterset_fields = ['parse_status', 'job']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('latest') == 'true':
            from ingestion.models import IngestionJob
            latest_job = IngestionJob.objects.order_by('-ingested_at').first()
            if latest_job:
                qs = qs.filter(job=latest_job)
        return qs

class NormalizedRecordViewSet(viewsets.ModelViewSet):
    queryset = NormalizedRecord.objects.all().order_by('-raw_record__job__ingested_at', 'id')
    serializer_class = NormalizedRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('latest') == 'true':
            from ingestion.models import IngestionJob
            latest_job = IngestionJob.objects.order_by('-ingested_at').first()
            if latest_job:
                qs = qs.filter(raw_record__job=latest_job)
        return qs

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        record = self.get_object()
        if record.is_locked:
            return Response({"error": "Record is locked"}, status=status.HTTP_400_BAD_REQUEST)
            
        record.review_status = 'FLAGGED'
        record.save()
        
        note = request.data.get('note', '')
        AuditLog.objects.create(
            record=record,
            action='FLAGGED',
            note=note
        )
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        record = self.get_object()
        if record.is_locked:
            return Response({"error": "Record is already locked"}, status=status.HTTP_400_BAD_REQUEST)
            
        record.review_status = 'APPROVED'
        record.is_locked = True
        record.save()
        
        AuditLog.objects.create(
            record=record,
            action='APPROVED'
        )
        return Response(self.get_serializer(record).data)
