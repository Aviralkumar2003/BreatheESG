import os
import csv
import random
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_samples_dir():
    d = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'samples')
    os.makedirs(d, exist_ok=True)
    return d

def generate_sap(out_dir):
    path = os.path.join(out_dir, 'sample_sap.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Buchungsdatum', 'Belegnummer', 'Werk', 'Materialnummer', 'Menge', 'Mengeneinheit'])
        start_date = datetime(2024, 1, 1)
        for i in range(55):
            date_str = (start_date + timedelta(days=i)).strftime('%d.%m.%Y')
            doc_no = f"4500{i:06d}"
            werk = random.choice(["1000", "2000", "3000"])
            mat = random.choice(["DIESEL-001", "PETROL-002", "PROC-OFFICE"])
            qty = round(random.uniform(10.0, 500.0), 2)
            unit = random.choice(["L", "ltr", "EA"])
            if i == 10:
                date_str = "InvalidDate" # Should be FAILED
            writer.writerow([date_str, doc_no, werk, mat, qty, unit])
    print(f"Generated {path}")

def generate_travel(out_dir):
    path = os.path.join(out_dir, 'sample_travel.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Employee_ID', 'Flight_Date', 'Origin_City', 'Arrival_City', 'Distance_km', 'Class'])
        start_date = datetime(2024, 1, 1)
        for i in range(55):
            emp = f"EMP-{random.randint(100, 999)}"
            f_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            orig = random.choice(["New York", "London", "Tokyo", "Paris", "Berlin"])
            dest = random.choice(["Los Angeles", "Dubai", "Singapore", "Sydney", "Rome"])
            dist = random.randint(500, 10000)
            cls = random.choice(["Economy", "Business", "First"])
            if i == 20:
                dest = "UNKNOWN" # Should be SUSPICIOUS
            writer.writerow([emp, f_date, orig, dest, dist, cls])
    print(f"Generated {path}")

def generate_utility(out_dir):
    path = os.path.join(out_dir, 'sample_utility.pdf')
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "MOCK UTILITY BILL")
    c.setFont("Helvetica", 10)
    
    y = 720
    for i in range(55):
        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750
        
        meter_id = f"MTR-{random.randint(1000, 9999)}"
        if i == 30:
            c.drawString(50, y, f"Meter ID: ") # Should be SUSPICIOUS
        else:
            c.drawString(50, y, f"Meter ID: {meter_id}")
            
        consumption = round(random.uniform(100.0, 5000.0), 2)
        if i == 40:
            c.drawString(200, y, f"Total Consumption: InvalidValue kWh") # Should be FAILED
        else:
            c.drawString(200, y, f"Total Consumption: {consumption} kWh")
        
        y -= 20
        
    c.save()
    print(f"Generated {path}")

if __name__ == '__main__':
    d = create_samples_dir()
    generate_sap(d)
    generate_travel(d)
    generate_utility(d)
