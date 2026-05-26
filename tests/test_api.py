import pytest
from rest_framework.test import APIClient
from clients.models import Client
from ingestion.models import IngestionJob
from records.models import RawRecord, NormalizedRecord

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def setup_data():
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(client=client, source_type='SAP', file_name='test.csv')
    raw = RawRecord.objects.create(job=job, raw_data={})
    norm = NormalizedRecord.objects.create(
        raw_record=raw, scope='SCOPE_1', quantity_original=100.0,
        unit_original='L', quantity_normalized=100.0, unit_normalized='L'
    )
    return client, job, norm

@pytest.mark.django_db
def test_client_endpoints(api_client):
    response = api_client.post('/api/clients/', {'name': 'New Client'})
    assert response.status_code == 201
    
    response = api_client.get('/api/clients/')
    assert response.status_code == 200
    assert len(response.data['results']) == 1

@pytest.mark.django_db
def test_job_endpoints(api_client, setup_data):
    client, job, _ = setup_data
    response = api_client.get('/api/ingestion/jobs/')
    assert response.status_code == 200
    assert len(response.data['results']) == 1

@pytest.mark.django_db
def test_record_endpoints(api_client, setup_data):
    client, job, norm = setup_data
    response = api_client.get('/api/records/')
    assert response.status_code == 200
    assert len(response.data['results']) == 1

@pytest.mark.django_db
def test_upload_endpoint(api_client, setup_data):
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    client, _, _ = setup_data
    csv_content = b"Buchungsdatum,Menge,Mengeneinheit\n15.01.2024,500,L\n"
    file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
    
    response = api_client.post(
        '/api/ingestion/jobs/upload/',
        {'client': client.id, 'source_type': 'SAP', 'file': file},
        format='multipart'
    )
    
    assert response.status_code == 201
    assert response.data['status'] == 'COMPLETE'
    assert response.data['row_count'] == 1

@pytest.mark.django_db
def test_record_actions(api_client, setup_data):
    client, job, norm = setup_data
    
    # Test flag
    response = api_client.post(f'/api/records/{norm.id}/flag/', {'note': 'Looks too high'})
    assert response.status_code == 200
    norm.refresh_from_db()
    assert norm.review_status == 'FLAGGED'
    assert norm.audit_logs.filter(action='FLAGGED').exists()
    
    # Test approve
    response = api_client.post(f'/api/records/{norm.id}/approve/')
    assert response.status_code == 200
    norm.refresh_from_db()
    assert norm.review_status == 'APPROVED'
    assert norm.is_locked is True
    assert norm.audit_logs.filter(action='APPROVED').exists()
