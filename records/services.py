from .models import NormalizedRecord

def normalize_record(raw_record):
    source_type = raw_record.job.source_type
    raw_data = raw_record.raw_data
    
    scope = 'SCOPE_3'
    qty = 0.0
    unit = 'unknown'
    norm_qty = 0.0
    norm_unit = 'kWh'
    
    if source_type == 'SAP':
        scope = 'SCOPE_1'
        qty = float(raw_data.get('Menge', 0))
        unit = raw_data.get('Mengeneinheit', 'L').strip()
        
        if unit.upper() in ['L', 'LTR']:
            norm_qty = qty * 10.0
        else:
            norm_qty = qty
            
    elif source_type == 'UTILITY':
        scope = 'SCOPE_2'
        qty = float(raw_data.get('Consumption', 0))
        unit = raw_data.get('Unit', 'kWh').strip()
        
        if unit.upper() == 'MWH':
            norm_qty = qty * 1000.0
        else:
            norm_qty = qty
            
    elif source_type == 'TRAVEL':
        scope = 'SCOPE_3'
        qty = float(raw_data.get('Amount', 0))
        unit = raw_data.get('Currency', 'USD').strip()
        norm_qty = qty * 0.5

    review_status = 'PENDING'
    flag_note = ''
    if raw_record.parse_status == 'SUSPICIOUS':
        review_status = 'FLAGGED'
        flag_note = raw_record.parse_error or 'Flagged during parsing'

    norm = NormalizedRecord.objects.create(
        raw_record=raw_record,
        scope=scope,
        quantity_original=qty,
        unit_original=unit,
        quantity_normalized=norm_qty,
        unit_normalized=norm_unit,
        review_status=review_status,
        flag_note=flag_note
    )
    return norm
