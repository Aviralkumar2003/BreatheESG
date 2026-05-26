import os
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.conf import settings
from .models import IngestionJob
from .serializers import IngestionJobSerializer
from .parsers.sap import parse_sap_file
from .parsers.utility import parse_utility_file
from .parsers.travel import parse_travel_file

# Metadata for each known sample file
SAMPLE_CATALOGUE = {
    "sample_sap.csv": {
        "name": "SAP Export — Fuel & Procurement",
        "description": "55 rows of German SAP fuel/procurement records with mixed units (L, ltr, EA). Includes one intentionally invalid date row to demonstrate error handling.",
        "source_type": "SAP",
    },
    "sample_travel.csv": {
        "name": "Travel / Flight Data",
        "description": "55 rows of corporate flight records across Economy, Business & First class. Includes one row with an 'UNKNOWN' destination flagged as suspicious.",
        "source_type": "TRAVEL",
    },
    "sample_utility.pdf": {
        "name": "Utility Bill — Electricity",
        "description": "55 meter readings extracted from a multi-page PDF utility bill. Includes one missing Meter ID (suspicious) and one invalid consumption value (failed).",
        "source_type": "UTILITY",
    },
}


class IngestionJobViewSet(viewsets.ModelViewSet):
    queryset = IngestionJob.objects.all()
    serializer_class = IngestionJobSerializer

    @action(detail=False, methods=['get'])
    def samples(self, request):
        """
        List all available sample files in the samples/ directory.
        Returns catalogue metadata merged with a live filesystem check.
        """
        samples_dir = Path(settings.BASE_DIR) / "samples"
        result = []

        for filename, meta in SAMPLE_CATALOGUE.items():
            file_path = samples_dir / filename
            result.append({
                "filename": filename,
                "name": meta["name"],
                "description": meta["description"],
                "source_type": meta["source_type"],
                "available": file_path.exists(),
            })

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def ingest_sample(self, request):
        """
        Ingest a pre-existing sample file from the samples/ directory.
        Accepts: { "client": <id>, "filename": "<sample_filename>" }
        """
        client_id = request.data.get('client')
        filename = request.data.get('filename')

        if not client_id or not filename:
            return Response({"error": "Missing required fields: client and filename"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent path traversal — only allow bare filenames from the catalogue
        if filename not in SAMPLE_CATALOGUE:
            return Response({"error": f"Unknown sample file: {filename}"}, status=status.HTTP_400_BAD_REQUEST)

        meta = SAMPLE_CATALOGUE[filename]
        source_type = meta["source_type"]
        samples_dir = Path(settings.BASE_DIR) / "samples"
        full_path = samples_dir / filename

        if not full_path.exists():
            return Response(
                {"error": f"Sample file '{filename}' not found on server. Run: python scripts/generate_samples.py"},
                status=status.HTTP_404_NOT_FOUND,
            )

        job = IngestionJob.objects.create(
            client_id=client_id,
            source_type=source_type,
            file_name=filename,
            status='PROCESSING'
        )

        try:
            if source_type == 'SAP':
                parse_sap_file(job, str(full_path))
            elif source_type == 'UTILITY':
                parse_utility_file(job, str(full_path))
            elif source_type == 'TRAVEL':
                parse_travel_file(job, str(full_path))
        except Exception as e:
            job.status = 'FAILED'
            job.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        job.refresh_from_db()
        serializer = self.get_serializer(job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
