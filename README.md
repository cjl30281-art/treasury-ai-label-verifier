# Treasury AI Alcohol Label Verifier

A proof-of-concept application for AI-assisted alcohol beverage label screening. It is intentionally focused on the supplied stakeholder priorities: **fast feedback, simple operation, batch handling, human judgment for ambiguity, and minimal dependence on outbound cloud services**.

## Core workflow
An agent enters expected application values and uploads one or more label images. The prototype:
- extracts label text with local Tesseract OCR;
- compares brand name, class/type, alcohol content, net contents, producer/bottler, and country of origin when applicable;
- performs a stricter Government Health Warning check;
- returns **PASS**, **HUMAN REVIEW**, or **ACTION NEEDED**;
- supports batch uploads and CSV results;
- reports processing time for each image.

## Why this architecture
**Local-first OCR:** The stakeholder notes warn that government networks may block external ML endpoints. The core app therefore requires no paid cloud AI API or secret key.

**Explainable rules:** Compliance checks should be auditable. The interface shows each field, result, detected evidence, and reason.

**Human in the loop:** Label review contains nuance. Ambiguous OCR/case variations are routed to human review instead of silently accepted.

**Batch support:** Multiple images can be screened in one session to address high-volume importer workflows.

## Technology
Python, Streamlit, Tesseract/pytesseract, Pillow, pandas.

## Run locally
Install Python 3.10+ and Tesseract OCR. On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```
Then:
```bash
git clone YOUR_REPOSITORY_URL
cd treasury-ai-label-verifier
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Windows activation:
```powershell
.venv\Scripts\activate
```

## Deploy on Streamlit Community Cloud
1. Push this repository to GitHub.
2. Create a new Streamlit Community Cloud app.
3. Select this repository, branch `main`, and entry point `app.py`.
4. Deploy. `packages.txt` installs Tesseract on the host.
5. Verify the public URL in an incognito/private browser.

No API keys or secrets are required.

## Tests
```bash
pip install pytest
pytest -q
```

## Assumptions
- This proof of concept demonstrates common label-field screening, not every beverage-specific TTB rule.
- Application values are entered manually because direct COLA integration is outside prototype scope.
- OCR is assistive: a missed OCR result is not proof that a field is absent.
- The warning receives stricter prescribed-language handling than ordinary brand/case differences.
- The prototype does not claim to prove bold weight, minimum type size, contrast, or every placement requirement from pixels alone.

## Performance
The UI reports per-image processing time because the stakeholder target is approximately five seconds. Actual performance depends on image size and hosting resources; no artificial performance claim is made.

## Privacy and security
Uploaded images are processed in memory by application code and are not intentionally persisted. No external AI API, database, authentication, PII workflow, or COLA integration is required. Production federal deployment would require formal security, privacy, records-retention, accessibility, infrastructure, and authorization review.

## Error handling
The upload control limits file types. Processing failures return a user-facing message rather than a stack trace. Ambiguous matches are routed to human review.

## Trade-offs and next steps
A production system should add beverage-specific rule engines; robust document AI for curved bottles, glare and perspective; visual checks for capitalization/boldness/type size/contrast/placement; structured COLA ingestion; audit logging and access control; approved federal hosting; accessibility/security testing; and benchmark datasets for accuracy, false decisions and latency.

The narrow prototype favors a complete, understandable workflow over an ambitious but fragile architecture.

## Regulatory note
This is a technical demonstration, **not an official TTB compliance determination**. Reviewers should consult current TTB regulations and guidance for authoritative requirements.
