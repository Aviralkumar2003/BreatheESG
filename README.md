# Breathe ESG Ingestion Platform

Breathe ESG is a prototype internal B2B dashboard built for Sustainability Analysts. 

Carbon accounting is famously difficult because the source data is notoriously messy. Analysts are handed thousands of rows of German SAP exports, unpredictable CSVs from travel vendors, and unstructured PDFs from utility companies. 

This platform solves the "Ingestion & Normalization" phase of carbon accounting. It provides a robust pipeline that parses these chaotic files, standardizes their units, categorizes their emission scopes, and surfaces them into a beautiful, paginated React dashboard where an analyst can flag suspicious rows or approve valid ones. 

Once a row is approved, it is cryptographically locked into an immutable audit trail, providing external auditors (like PwC or Deloitte) with a provable chain of custody from the final calculation all the way back to the exact JSON extracted from the original uploaded PDF.

---

## Extensive Documentation

We have deeply documented the architectural and product decisions of this platform. Please refer to the following documents in the `docs/` directory:

1. **`docs/ARCHITECTURE.md`**: The complete technical breakdown. Read this to understand the Tech Stack (Django/React), the alternative frameworks we rejected, the exact responsibility of every folder, and a Mermaid flowchart of how data moves through the system.
2. **`docs/MODEL.md`**: An explanation of our Database schema. Read this to understand how we handle multi-tenancy (scoping to Clients), standardizing units, and enforcing immutability.
3. **`docs/DECISIONS.md`**: An explanation of the ambiguous product decisions we had to make, what we chose, and what questions we would ask a Product Manager in a real-world scenario.
4. **`docs/SOURCES.md`**: A deep dive into the three data sources we support (SAP, Utility PDFs, Travel CSVs), what they look like in reality, and how our parsers extract them.
5. **`docs/TRADEOFFS.md`**: Three major features we deliberately chose *not* to build in this prototype to save time, and how we would build them in production.

---

## How to Run Locally (Windows/PowerShell)

### 1. Start the Django Backend
Open a PowerShell terminal in the root directory.

```powershell
# 1. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 2. (Optional) Run the test suite to ensure the pipeline is healthy
python -m pytest

# 3. Start the backend server on port 8000
python manage.py runserver
```

### 2. Start the React Frontend
Open a *second* PowerShell terminal and navigate to the frontend folder.

```powershell
cd frontend

# 1. Install Node dependencies (if not already installed)
npm install

# 2. Start the Vite development server
npm run dev
```

### 3. Usage Guide
1. Open your browser to `http://localhost:5173`.
2. Ensure you have the test files ready (they are located in the `/tests/fixtures/` folder: `sample_sap.csv`, `sample_travel.csv`, `sample_utility.pdf`).
3. Select a Client (e.g. "Acme Corp") and the appropriate source type.
4. Upload the file. You will see a success message indicating how many rows were parsed.
5. Click **Go to Review Dashboard**. 
6. Observe the Normalized table. Notice how heterogeneous fuel units were converted to `kWh`. 
7. Click **Approve** on a row. Notice how the row becomes "Locked"—this ensures immutability for the auditors.
8. Click **View Failed & Suspicious Rows**. Observe how rows that were missing critical metadata (like an Arrival City) were gracefully caught and surfaced to the analyst, ensuring zero data loss.
