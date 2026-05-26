import pytest
from clients.models import Client
from ingestion.models import IngestionJob
from records.models import RawRecord

@pytest.mark.django_db
def test_create_raw_record():
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(
        client=client, source_type='SAP', file_name='test.csv'
    )
    raw = RawRecord.objects.create(
        job=job,
        raw_data={"foo": "bar"},
        parse_status='OK'
    )
    assert raw.job == job
    assert raw.raw_data == {"foo": "bar"}
    assert raw.parse_status == 'OK'
    assert raw.id is not None

@pytest.mark.django_db
def test_create_normalized_record():
    from records.models import NormalizedRecord
    from django.core.exceptions import ValidationError
    
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(client=client, source_type='SAP', file_name='test.csv')
    raw = RawRecord.objects.create(job=job, raw_data={})
    
    norm = NormalizedRecord.objects.create(
        raw_record=raw,
        scope='SCOPE_1',
        quantity_original=100.0,
        unit_original='L',
        quantity_normalized=100.0,
        unit_normalized='L'
    )
    assert norm.scope == 'SCOPE_1'
    assert not norm.is_locked
    
    # Test immutability
    norm.is_locked = True
    norm.save()
    
    norm.quantity_normalized = 200.0
    with pytest.raises(ValidationError):
        norm.save()

@pytest.mark.django_db
def test_create_audit_log():
    from records.models import AuditLog, NormalizedRecord
    
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(client=client, source_type='SAP', file_name='test.csv')
    raw = RawRecord.objects.create(job=job, raw_data={})
    norm = NormalizedRecord.objects.create(
        raw_record=raw,
        scope='SCOPE_1',
        quantity_original=100.0,
        unit_original='L',
        quantity_normalized=100.0,
        unit_normalized='L'
    )
    
    log = AuditLog.objects.create(
        record=norm,
        action='INGESTED',
        actor='system',
        new_value={"status": "PENDING"}
    )
    assert log.action == 'INGESTED'
    assert log.record == norm

@pytest.mark.django_db
def test_normalize_sap_record():
    from records.services import normalize_record
    
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(client=client, source_type='SAP', file_name='test.csv')
    raw = RawRecord.objects.create(job=job, raw_data={
        "Buchungsdatum": "15.01.2024",
        "Menge": "500",
        "Mengeneinheit": "L"
    }, parse_status='OK')
    
    norm = normalize_record(raw)
    
    assert norm.scope == 'SCOPE_1'
    assert norm.quantity_original == 500
    assert norm.unit_original.upper() == 'L'
    assert norm.unit_normalized == 'kWh'
    # diesel approx 10 kWh per liter
    assert norm.quantity_normalized == 5000

@pytest.mark.django_db
def test_normalize_utility_record():
    from records.services import normalize_record
    
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(client=client, source_type='UTILITY', file_name='test.csv')
    raw = RawRecord.objects.create(job=job, raw_data={
        "Consumption": "12.5",
        "Unit": "MWh"
    }, parse_status='OK')
    
    norm = normalize_record(raw)
    
    assert norm.scope == 'SCOPE_2'
    assert norm.quantity_original == 12.5
    assert norm.unit_original.upper() == 'MWH'
    assert norm.unit_normalized == 'kWh'
    assert norm.quantity_normalized == 12500
