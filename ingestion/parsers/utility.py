import re
from pypdf import PdfReader
from records.models import RawRecord
from records.services import normalize_record

def parse_utility_file(job, file_path):
    success = 0
    error = 0
    suspicious = 0
    row_count = 0
    
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        meters = list(re.finditer(r"Meter ID:\s*([A-Za-z0-9-]+)", text, re.IGNORECASE))
        consumptions = list(re.finditer(r"Total Consumption:\s*([0-9.]+)\s*([A-Za-z]+)", text, re.IGNORECASE))
        
        row_count = max(len(meters), len(consumptions), 1)
        
        for i in range(row_count):
            m_match = meters[i] if i < len(meters) else None
            c_match = consumptions[i] if i < len(consumptions) else None
            
            raw_data = {
                "Meter_ID": m_match.group(1) if m_match else None,
                "Consumption": c_match.group(1) if c_match else None,
                "Unit": c_match.group(2) if c_match else None,
                "Full_Text": text[:1000]
            }
            
            try:
                if not raw_data["Consumption"]:
                    raise ValueError("Could not extract consumption")
                float(raw_data["Consumption"])
                
                if not raw_data["Meter_ID"]:
                    raw = RawRecord.objects.create(job=job, raw_data=raw_data, parse_status='SUSPICIOUS', parse_error="Missing Meter_ID")
                    suspicious += 1
                else:
                    raw = RawRecord.objects.create(job=job, raw_data=raw_data, parse_status='OK')
                    success += 1
                
                normalize_record(raw)
            except Exception as row_e:
                RawRecord.objects.create(job=job, raw_data=raw_data, parse_status='FAILED', parse_error=str(row_e))
                error += 1
            
    except Exception as e:
        RawRecord.objects.create(job=job, raw_data={"error": str(e)}, parse_status='FAILED', parse_error=str(e))
        error += 1
        
    job.row_count = row_count
    job.success_count = success
    job.error_count = error
    job.status = 'COMPLETE'
    job.save()
