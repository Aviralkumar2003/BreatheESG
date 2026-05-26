import csv
from datetime import datetime
from records.models import RawRecord

def parse_date(date_str):
    for fmt in ('%d.%m.%Y', '%Y%m%d', '%m/%d/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    raise ValueError('Invalid date')

def parse_sap_file(job, file_path):
    success = 0
    error = 0
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
                date_str = raw_data.get('Buchungsdatum')
                if not date_str:
                    raise ValueError("Missing date")
                parse_date(date_str)
                
                raw = RawRecord.objects.create(
                    job=job,
                    raw_data=raw_data,
                    parse_status='OK'
                )
                from records.services import normalize_record
                normalize_record(raw)
                success += 1
            except Exception as e:
                RawRecord.objects.create(
                    job=job,
                    raw_data=raw_data,
                    parse_status='FAILED',
                    parse_error=str(e)
                )
                error += 1
                
    job.row_count = row_count
    job.success_count = success
    job.error_count = error
    job.status = 'COMPLETE'
    job.save()
