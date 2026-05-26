# Database Models

Carbon accounting requires strict adherence to data integrity. If an auditor cannot trace a final emission number back to a specific client, a specific upload batch, and a specific raw JSON payload, the platform fails compliance. 

This document explains the rationale behind the Django models located in `clients/models.py`, `ingestion/models.py`, and `records/models.py`.

## 1. `Client` (Multi-Tenancy)
**Fields**: `id`, `name`, `plant_code_map`, `created_at`
**Why**: Carbon accounting platforms are B2B SaaS. We cannot mix data from Acme Corp with data from Globex. Every single data model in the system cascades down from the `Client` model.
**Detail**: The `plant_code_map` is a JSON field designed to solve a specific ERP problem: SAP often exports locations as internal codes (e.g., "PL100"). The normalizer can use this map to translate "PL100" into "Berlin HQ" based on the specific client's configuration.

## 2. `IngestionJob` (Batch Tracking)
**Fields**: `id`, `client`, `source_type`, `status`, `row_count`, `success_count`, `error_count`, `ingested_at`
**Why**: Analysts do not upload data one row at a time; they upload massive CSVs and PDFs. We need a way to track the health of a specific upload batch.
**Detail**: If a file contains 10,000 rows and 50 of them fail to parse, the `error_count` explicitly surfaces this to the analyst. The `source_type` (SAP, UTILITY, TRAVEL) dictates which python parser is invoked.

## 3. `RawRecord` (The Immutable Source)
**Fields**: `id`, `job`, `row_index`, `raw_data` (JSON), `parse_status`, `parse_error`
**Why**: We must never throw away the original data, even if it is horribly malformed. The `RawRecord` is a literal, un-opinionated JSON dump of exactly what the python parser found on that specific row of the CSV or PDF. 
**Detail**: If the normalizer breaks or the parsing rules change next year, we can simply run a script to re-normalize all the `RawRecords` because we saved the raw `JSON`. If `parse_status` is marked as `FAILED`, the record skips normalization entirely and is surfaced in the "Failed Records" UI.

## 4. `NormalizedRecord` (The Standardized Ledger)
**Fields**: `id`, `raw_record`, `scope`, `quantity_original`, `unit_original`, `quantity_normalized`, `unit_normalized` (always `kWh`), `review_status`, `is_locked`, `flag_note`
**Why**: You cannot sum "Gallons of Diesel", "Liters of Jet Fuel", and "Megawatts of Electricity" together. The Normalizer translates the flexible JSON of the `RawRecord` into a strict, strongly-typed ledger. 
**Detail**: 
- **Scope Categorization**: Automatically categorizes as `SCOPE_1` (Direct Fuel), `SCOPE_2` (Purchased Electricity), or `SCOPE_3` (Value Chain/Travel).
- **Unit Normalization**: Translates all energy variants (Liters, MWh, etc) into a canonical baseline (`kWh`) so the downstream calculation engine can apply emission factors easily.
- **Immutability (`is_locked`)**: When an analyst approves a row, `is_locked` flips to `True`. The Django `save()` method is overridden to throw a hard Exception if anyone attempts to modify a locked row. This guarantees auditor compliance.

## 5. `AuditLog` (The Chain of Custody)
**Fields**: `id`, `record`, `action`, `performed_by`, `timestamp`, `notes`
**Why**: When an external auditor asks "Who approved this 1,000 kWh usage?", we must be able to prove it.
**Detail**: Every time a `NormalizedRecord` changes state (e.g. `PENDING` -> `APPROVED`), an `AuditLog` entry is appended. This creates an append-only cryptographic-style ledger of human actions.
