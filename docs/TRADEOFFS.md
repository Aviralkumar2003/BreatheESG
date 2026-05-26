# Engineering Tradeoffs

Given the time constraints of building a functional prototype, we had to make deliberate decisions about what *not* to build. Here are the three most significant tradeoffs we made, why we made them, and how we would implement them in a production environment.

## 1. Synchronous I/O for File Uploads
**What we did**: When a user uploads a CSV or PDF, the Django view `IngestionJobViewSet.upload` holds the HTTP request open while it synchronously reads the file, parses every row, and writes to the SQLite database.
**How it breaks in reality**: If an analyst uploads a 1-million row CSV, the HTTP request will time out before the parsing finishes, returning a 504 Gateway Timeout error, even though the server might still be churning in the background. 
**The Production Solution**: We would immediately move to an asynchronous architecture. The upload endpoint would immediately save the file to an S3 bucket, create an `IngestionJob` with a status of `QUEUED`, and return a 202 Accepted. A Celery worker would pick up the task, parse the file, and update the job status. The React frontend would poll or use WebSockets to show a progress bar.

## 2. Lack of Authentication & Authorization (RBAC)
**What we did**: The API is completely open. Any POST request to `/approve/` is accepted, and the `AuditLog` currently hardcodes the `performed_by` field to "System" or a generic user.
**Why we didn't build it properly**: Implementing JWT tokens, login screens, and user models is boilerplate table-stakes. We prioritized building the carbon-specific domain logic (unit conversion, scoping, audit locks).
**How it breaks in reality**: An auditor cannot trust an `AuditLog` if there is no cryptographic proof that "Analyst Sarah" was actually logged in and authorized to approve that specific client's data. Furthermore, an analyst from Client A could theoretically query the API for Client B's data (a massive security breach).
**The Production Solution**: We would implement Django REST Framework SimpleJWT. We would enforce Row-Level Security (RLS) or strict queryset filtering so that users can only view `IngestionJobs` and `NormalizedRecords` that belong to their assigned `Client` IDs.

## 3. SQLite and a Single Monolithic App
**What we did**: We used the default SQLite file-based database and grouped everything into a single Django monolith.
**Why we didn't build it properly**: Setting up Docker, PostgreSQL, and connection pooling takes time. SQLite requires zero configuration.
**How it breaks in reality**: SQLite locks the entire database file on write operations. If 10 analysts are approving records simultaneously, the database will throw "Database is locked" exceptions. 
**The Production Solution**: We would migrate to a managed PostgreSQL database (e.g. AWS RDS). PostgreSQL handles high-concurrency writes flawlessly. If the application grew massively, we might even split the heavy I/O ingestion parser into a Go or Rust microservice, while keeping the complex business logic (Normalization and Approval) in the Django monolith.
