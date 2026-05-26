# Product & Engineering Decisions

When building a zero-to-one prototype for a complex, heavily-regulated domain like Carbon Accounting, several ambiguities arise. This document outlines the core ambiguities we faced, how we resolved them, and the questions we would escalate to a Product Manager if we were building this for a live production environment.

## 1. When does data become immutable?
**The Ambiguity**: Carbon accounting requires an audit trail. If an analyst modifies a value to fix a typo, is that a destructive edit, or does it require an entirely new versioned row?
**Our Decision**: We decided on an "Approval Lock". The `NormalizedRecord` model has an `is_locked` boolean. The analyst can view and theoretically flag the data as much as they want while it is `PENDING`. However, the moment they click `Approve`, the system sets `is_locked=True`. From that millisecond forward, the Django `save()` method throws a hard exception if any code attempts to modify the row. 
**PM Escalation Question**: *If a user realizes they approved a row with a typo, what is the exact product flow to undo that? Do we allow an "Admin Override Unlock", or do we force them to upload a negative "reversal" row (similar to double-entry accounting)?*

## 2. Handling Corrupted vs. "Suspicious" Data
**The Ambiguity**: SAP files and Travel CSVs are notoriously messy. What happens if a row is missing a critical numerical value (like "Total Cost") vs missing a non-critical dimension (like "Arrival City")? Should we drop the row entirely?
**Our Decision**: We instituted a two-tier failure system to ensure zero data loss.
- **`FAILED` (Corrupted)**: If the parser physically cannot extract the `Quantity` or `Unit` (e.g. the PDF is mangled), the row is marked as `FAILED`. It is saved as a `RawRecord` but is **not** passed to the Normalizer.
- **`SUSPICIOUS` (Incomplete)**: If the row is missing a non-critical metadata field (like Arrival City in our Travel parser), we mark it as `SUSPICIOUS`, but we **do** pass it to the Normalizer. The Normalizer automatically flags it in the Analyst Dashboard. This preserves the numerical carbon data while alerting the human that the metadata is incomplete.
**PM Escalation Question**: *Can we define a strict matrix of which exact fields are "Mandatory for Normalization" versus which fields are "Optional but require an analyst flag"?*

## 3. Paginating the Data Grid
**The Ambiguity**: The initial prototype loaded all `NormalizedRecords` into an array and fed them to React. This was fine for 10 rows, but enterprise clients upload CSVs with 100,000 rows. The browser would instantly crash due to an out-of-memory error.
**Our Decision**: We enabled global `PageNumberPagination` in Django REST Framework. This changed the JSON payload from a flat array `[]` to an object with `{ count, next, previous, results: [] }`. We completely rewrote the React components (`ReviewDashboard` and `FailedRecords`) to render `data.results` and provide `<Previous>` and `<Next>` buttons that fetch the adjacent URL.
**PM Escalation Question**: *Server-side pagination solves the memory issue, but it makes sorting and filtering much harder. Do we want to implement server-side sorting (e.g. `?ordering=-quantity`) or invest in a heavier data-grid library like AG-Grid?*

## 4. The Separation of Parsers and Normalizers
**The Ambiguity**: Should the `sap.py` parser also be responsible for converting units (e.g. Liters to kWh)?
**Our Decision**: Absolutely not. We strictly separated concerns. 
- The `parsers/` folder is exclusively responsible for I/O: reading the CSV/PDF string and dumping it into a schema-less `RawRecord` JSON field. 
- The `services.py` (Normalizer) is exclusively responsible for business logic: reading the JSON field and standardizing the units. 
This means if a new parser is added tomorrow (e.g. an API integration with Concur), the business logic for standardizing Scope 3 travel emissions does not need to be rewritten.
