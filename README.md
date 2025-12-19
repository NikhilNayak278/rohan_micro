# FHIR Harmonization Microservice

A Python/Flask microservice for mapping legacy data to FHIR R4 and harmonizing FHIR resources.

## Features

- **Mapping**: Converts legacy JSON payloads to FHIR R4 Bundles (Patient + Observations).
- **Harmonization**: Normalizes FHIR resources (e.g., Title Case names, standardizing tags).
- **Dockerized**: Ready for deployment.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Locally**
   ```bash
   python app.py
   ```
   Server runs on `http://localhost:5000`.

3. **Run with Docker**
   ```bash
   docker-compose up --build
   ```

## API Specification

### `POST /api/v1/map`
Maps legacy data to FHIR.

**Request:**
```json
{
    "id": "123",
    "first_name": "JOHN",
    "last_name": "DOE",
    "dob": "1980-01-01",
    "gender": "M",
    "blood_pressure": "120/80"
}
```

**Response:** FHIR Bundle (JSON)

### `POST /api/v1/harmonize`
Harmonizes a FHIR Bundle.

**Request:** FHIR Bundle (JSON)

**Response:** FHIR Bundle (JSON) with normalized fields and "harmonized" tag.

## Testing

Run unit tests:
```bash
pytest
```
