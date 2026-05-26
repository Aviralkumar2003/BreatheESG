# Breathe ESG Ingestion Platform

Breathe ESG is a prototype internal B2B dashboard built for Sustainability Analysts. 

Carbon accounting is famously difficult because the source data is notoriously messy. Analysts are handed thousands of rows of German SAP exports, unpredictable CSVs from travel vendors, and unstructured PDFs from utility companies. 

This platform solves the **Ingestion & Normalization** phase of carbon accounting. It provides a robust pipeline that parses these chaotic files, standardizes their units, categorizes their emission scopes, and surfaces them into a beautiful, paginated React dashboard where an analyst can flag suspicious rows or approve valid ones. 

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

## Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Git**

---

## How to Run Locally (Windows / PowerShell)

### Step 1 — Clone the Repository

```powershell
git clone https://github.com/Aviralkumar2003/BreatheESG.git
cd BreatheESG
```

---

### Step 2 — Set Up the Python Virtual Environment

```powershell
# Create a virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

> **Note:** If you get an execution policy error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

### Step 3 — Install Python Dependencies

```powershell
pip install -r requirements.txt
```

---

### Step 4 — Run Database Migrations

This creates the SQLite database and all required tables.

```powershell
python manage.py migrate
```

---

### Step 5 — Seed the Database

This populates the database with the three demo clients (**Acme Corp**, **Globex Corporation**, **Stark Industries**) that are required for uploading files through the UI.

```powershell
python scripts/seed.py
```

Expected output:
```
Seeding database...
Created client: Acme Corp
Created client: Globex Corporation
Created client: Stark Industries
Seeding complete.
```

> If you run it again, it will skip already-existing clients without erroring.

---

### Step 6 — Generate Sample Test Files

This generates three realistic sample files in the `samples/` directory that you can upload through the dashboard:

| File | Type | Description |
|------|------|-------------|
| `samples/sample_sap.csv` | SAP Export | 55 rows of fuel consumption data in German format, including an intentionally invalid date row |
| `samples/sample_travel.csv` | Travel CSV | 55 rows of flight records, including a suspicious "UNKNOWN" destination |
| `samples/sample_utility.pdf` | Utility Bill PDF | 55 meter readings across multiple pages, including a missing meter ID and an invalid consumption value |

```powershell
python scripts/generate_samples.py
```

Expected output:
```
Generated ...\samples\sample_sap.csv
Generated ...\samples\sample_travel.csv
Generated ...\samples\sample_utility.pdf
```

---

### Step 7 — (Optional) Run the Test Suite

```powershell
python -m pytest
```

---

### Step 8 — Start the Django Backend

```powershell
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

---

### Step 9 — Start the React Frontend

Open a **second** PowerShell terminal in the project root.

```powershell
cd frontend

# Install Node dependencies (only needed once)
npm install

# Start the Vite dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Quick-Start Cheat Sheet

After the one-time setup (Steps 1–6), you only need to run these two commands in two separate terminals:

**Terminal 1 (Backend):**
```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

---

## Usage Guide

1. Open your browser to `http://localhost:5173`.
2. Select a **Client** (e.g. "Acme Corp") and the appropriate **Source Type**.
3. Upload one of the files from the `samples/` folder.
4. You will see a success message indicating how many rows were parsed.
5. Click **Go to Review Dashboard**.
6. Observe the Normalized table — notice how heterogeneous fuel units were converted to `kWh`.
7. Click **Approve** on a row. Notice how the row becomes "Locked" — this ensures immutability for auditors.
8. Click **View Failed & Suspicious Rows**. Observe how rows missing critical metadata (like an Arrival City) were gracefully caught and surfaced to the analyst, ensuring zero data loss.
