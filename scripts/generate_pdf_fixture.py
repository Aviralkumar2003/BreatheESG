import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_utility_pdf(filepath):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "MOCK UTILITY BILL")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, "Customer: Acme Corp")
    c.drawString(50, 680, "Meter ID: MTR-9981")
    c.drawString(50, 660, "Billing Period: 2024-01-15 to 2024-02-14")
    c.drawString(50, 640, "Tariff Code: COM-ELEC")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 600, "Usage Summary:")
    c.setFont("Helvetica", 12)
    c.drawString(50, 580, "Total Consumption: 4500 kWh")
    c.drawString(50, 560, "Amount Due: $450.00")
    
    c.save()
    print(f"Generated PDF fixture at: {filepath}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(current_dir, "tests", "fixtures", "sample_utility.pdf")
    generate_utility_pdf(target_path)
