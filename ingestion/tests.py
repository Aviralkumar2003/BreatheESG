import pytest
from clients.models import Client
from ingestion.models import IngestionJob


@pytest.mark.django_db
def test_create_ingestion_job():
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(
        client=client,
        source_type='SAP',
        file_name='test.csv',
        status='PENDING',
        row_count=10,
        success_count=0,
        error_count=0
    )
    assert job.client == client
    assert job.source_type == 'SAP'
    assert job.file_name == 'test.csv'
    assert job.status == 'PENDING'
    assert job.row_count == 10
