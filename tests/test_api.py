import pytest
import json
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_map_legacy_patient(client):
    legacy_data = {
        "id": "123",
        "first_name": "JOHN",
        "last_name": "DOE",
        "dob": "1980-01-01",
        "gender": "M",
        "blood_pressure": "120/80"
    }
    
    response = client.post('/api/v1/map', 
                         data=json.dumps(legacy_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = response.json
    assert data['resourceType'] == 'Bundle'
    
    # Check Patient
    patient = next(e['resource'] for e in data['entry'] if e['resource']['resourceType'] == 'Patient')
    assert patient['name'][0]['family'] == 'DOE'  # Raw mapping keeps case
    assert patient['gender'] == 'male'

def test_harmonize_patient(client):
    # Create a raw FHIR patient with uppercase name
    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "123",
                    "name": [{"family": "DOE", "given": ["JOHN"]}],
                    "gender": "male"
                },
                "request": {"method": "POST", "url": "Patient"}
            }
        ]
    }
    
    response = client.post('/api/v1/harmonize',
                          data=json.dumps(fhir_bundle),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.json
    
    patient = next(e['resource'] for e in data['entry'] if e['resource']['resourceType'] == 'Patient')
    # Check harmonization (Title Case)
    assert patient['name'][0]['family'] == 'Doe'
    assert patient['name'][0]['given'][0] == 'John'
    # Check tag
    assert patient['meta']['tag'][0]['code'] == 'harmonized'
