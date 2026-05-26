import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from .models import IngestionJob
from .serializers import IngestionJobSerializer
from .parsers.sap import parse_sap_file
from .parsers.utility import parse_utility_file
from .parsers.travel import parse_travel_file

class IngestionJobViewSet(viewsets.ModelViewSet):
    queryset = IngestionJob.objects.all()
    serializer_class = IngestionJobSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        client_id = request.data.get('client')
        source_type = request.data.get('source_type')
        uploaded_file = request.FILES.get('file')

        if not all([client_id, source_type, uploaded_file]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        job = IngestionJob.objects.create(
            client_id=client_id,
            source_type=source_type,
            file_name=uploaded_file.name,
            status='PROCESSING'
        )

        temp_path = default_storage.save(f"tmp/{uploaded_file.name}", uploaded_file)
        full_temp_path = default_storage.path(temp_path)

        try:
            if source_type == 'SAP':
                parse_sap_file(job, full_temp_path)
            elif source_type == 'UTILITY':
                parse_utility_file(job, full_temp_path)
            elif source_type == 'TRAVEL':
                parse_travel_file(job, full_temp_path)
            else:
                job.status = 'FAILED'
                job.save()
                return Response({"error": "Invalid source_type"}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if os.path.exists(full_temp_path):
                os.remove(full_temp_path)

        job.refresh_from_db()
        serializer = self.get_serializer(job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def reset(self, request):
        IngestionJob.objects.all().delete()
        return Response({"status": "All data reset successfully"}, status=status.HTTP_200_OK)
