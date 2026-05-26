# Data Sources & Parsing Reality

Carbon accounting requires ingesting data from a wide variety of enterprise systems. For this prototype, we modeled three distinct, highly realistic data sources. 

Here is what we learned from our research into these real-world formats, what our sample data looks like, and what would break in a real deployment if not properly handled.

## 1. SAP Exports (Fuel & Procurement)
**The Reality**: 
SAP is the backbone of global enterprise logistics. When facilities teams export fuel purchase data from SAP ERP, they usually get flat CSV files (or IDocs). 
- **Column Headers**: SAP is built in Germany. Even in English setups, headers are often exported as `Buchungsdatum` (Posting Date), `Werk` (Plant Code), and `Menge` (Quantity). 
- **Inconsistencies**: Plant codes are internal (e.g., `PL100`), not geographic addresses. Units are highly fragmented (Liters, Gallons, Tonnes).

**Our Implementation**: 
- `sample_sap.csv` contains German headers. 
- The `sap.py` parser maps these headers (`Menge` -> `Quantity`, `MEINS` -> `Unit`).
- It relies on the `Client.plant_code_map` JSON field to translate `PL100` into a real location later in the pipeline.

**What Would Break in Production**: 
If an SAP Admin changes the export variant layout in their ERP, the column headers might shift or be renamed entirely. A production system must allow analysts to "map" columns visually in the UI rather than hardcoding German headers in the Python parser.

## 2. Utility Portals (Electricity PDFs)
**The Reality**:
Most property managers do not get neat CSV APIs from their local power companies (e.g., PG&E or ConEdison). They log into a portal and download a PDF bill.
- **The Format**: PDFs are unstructured drawing instructions, not tables.
- **Inconsistencies**: Billing periods rarely align with calendar months (e.g., "Jan 14 to Feb 12"), making monthly carbon allocations extremely difficult.

**Our Implementation**:
- We built a `generate_pdf_fixture.py` script to generate a fake "Breathe Energy" bill.
- The `utility.py` parser uses `pypdf` to extract the raw text blocks and relies on Regex (e.g. `r"Total Consumption:\s*([0-9.]+)"`) to scrape the consumption values and Meter IDs.

**What Would Break in Production**:
Regex against PDFs is notoriously brittle. If the utility company adds a space or changes their font/layout (e.g., "Total Monthly Consumption:" instead of "Total Consumption:"), the Regex will fail. A production system would need a robust OCR engine (like AWS Textract) or a machine-learning model trained to identify bounding boxes around key-value pairs, rather than relying purely on text-based Regex.

## 3. Concur/Navan Corporate Travel (CSV)
**The Reality**:
Scope 3 emissions include employee business travel. Companies export this from Concur or Navan.
- **The Format**: Usually a CSV containing Expense Types, Amounts, and sometimes geographic data.
- **Inconsistencies**: Distances are rarely provided. Often you only get Airport Codes (e.g., SFO to JFK), meaning the downstream calculation engine has to calculate the Haversine distance itself before applying an emission factor. Sometimes data is just missing entirely (e.g. "Unknown" destination for a taxi receipt).

**Our Implementation**:
- `sample_travel.csv` includes an intentional error (an "UNKNOWN" arrival city).
- The `travel.py` parser gracefully catches this. It extracts the row but flags it as `SUSPICIOUS`, ensuring it passes to the normalizer without crashing.

**What Would Break in Production**:
Employees frequently miscategorize expenses (e.g., categorizing a client dinner as "Air Travel"). If we blindly parse the "Expense Type" column, we will apply massive aviation emission factors to a steak dinner. A production system requires an anomaly detection layer to flag expenses whose monetary cost does not align with the standard physical cost of the claimed travel mode.
