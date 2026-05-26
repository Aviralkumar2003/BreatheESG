import csv
from records.models import RawRecord

def parse_travel_file(job, file_path):
    success = 0
    error = 0
    suspicious = 0
    row_count = 0
    
    encoding = 'utf-8-sig'
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            _ = reader.fieldnames
    except UnicodeDecodeError:
        encoding = 'cp1252'
        
    with open(file_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            raw_data = dict(row)
            try:
                arr_city = raw_data.get('Arrival_City', '')
                if arr_city.upper() == 'UNKNOWN':
                    raw = RawRecord.objects.create(job=job, raw_data=raw_data, parse_status='SUSPICIOUS', parse_error="Unknown arrival city")
                    suspicious += 1
                else:
                    raw = RawRecord.objects.create(job=job, raw_data=raw_data, parse_status='OK')
                    success += 1
                
                from records.services import normalize_record
                normalize_record(raw)
            except Exception as e:
                RawRecord.objects.create(job=job, raw_data=raw_data, parse_status='FAILED', parse_error=str(e))
                error += 1
                
    job.row_count = row_count
    job.success_count = success
    job.error_count = error
    job.status = 'COMPLETE'
    job.save()
