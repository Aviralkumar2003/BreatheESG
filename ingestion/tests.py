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

@pytest.mark.django_db
def test_sap_parser():
    import os
    from ingestion.parsers.sap import parse_sap_file
    from records.models import RawRecord
    
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(client=client, source_type='SAP', file_name='sample_sap.csv')
    
    # Path to the sample file created earlier
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'fixtures', 'sample_sap.csv')
    
    # Run the parser
    parse_sap_file(job, file_path)
    
    job.refresh_from_db()
    assert job.status == 'COMPLETE'
    assert job.row_count == 6
    assert job.success_count == 5
    assert job.error_count == 1
    
    # Check that RawRecords were created
    assert RawRecord.objects.filter(job=job, parse_status='OK').count() == 5
    assert RawRecord.objects.filter(job=job, parse_status='FAILED').count() == 1

@pytest.mark.django_db
def test_utility_parser():
    import os
    from ingestion.parsers.utility import parse_utility_file
    from records.models import RawRecord
    
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(client=client, source_type='UTILITY', file_name='sample_utility.pdf')
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'fixtures', 'sample_utility.pdf')
    
    # If the PDF fixture doesn't exist for some reason during tests, generate it
    if not os.path.exists(file_path):
        import sys
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
        sys.path.append(scripts_dir)
        from generate_pdf_fixture import generate_utility_pdf
        generate_utility_pdf(file_path)
    
    parse_utility_file(job, file_path)
    job.refresh_from_db()
    
    assert job.status == 'COMPLETE'
    assert job.row_count == 1
    assert RawRecord.objects.filter(job=job, parse_status='OK').count() == 1

@pytest.mark.django_db
def test_travel_parser():
    import os
    from ingestion.parsers.travel import parse_travel_file
    from records.models import RawRecord
    
    client = Client.objects.create(name="Test Client")
    job = IngestionJob.objects.create(client=client, source_type='TRAVEL', file_name='sample_travel.csv')
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'fixtures', 'sample_travel.csv')
    
    parse_travel_file(job, file_path)
    job.refresh_from_db()
    
    assert job.status == 'COMPLETE'
    assert job.row_count == 4
    # 1 unknown arrival city -> suspicious. Others ok.
    assert RawRecord.objects.filter(job=job, parse_status='OK').count() == 3
    assert RawRecord.objects.filter(job=job, parse_status='SUSPICIOUS').count() == 1
