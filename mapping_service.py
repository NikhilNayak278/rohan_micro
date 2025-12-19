import logging
import uuid
from datetime import datetime
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.observation import Observation

logger = logging.getLogger(__name__)

class MappingService:
    @staticmethod
    def map_legacy_to_fhir(legacy_data):
        """
        Maps legacy patient data to FHIR Bundle containing Patient and Observations.
        Expected legacy format:
        {
            "id": "123",
            "first_name": "John",
            "last_name": "Doe",
            "dob": "1980-01-01",
            "gender": "M",
            "blood_pressure": "120/80"
        }
        """
        try:
            bundle_entries = []
            
            # Map Patient
            patient = Patient.model_construct()
            patient.id = str(legacy_data.get('id', uuid.uuid4()))
            
            name = HumanName.model_construct()
            name.family = legacy_data.get('last_name')
            name.given = [legacy_data.get('first_name')]
            patient.name = [name]
            
            gender_map = {'M': 'male', 'F': 'female', 'O': 'other'}
            patient.gender = gender_map.get(legacy_data.get('gender'), 'unknown')
            
            patient.birthDate = legacy_data.get('dob')
            
            bundle_entries.append(BundleEntry(resource=patient, request={'method': 'POST', 'url': 'Patient'}))
            
            # Map Blood Pressure if present
            bp_raw = legacy_data.get('blood_pressure')
            if bp_raw:
                try:
                    systolic, diastolic = bp_raw.split('/')
                    observation = Observation.model_construct()
                    observation.status = 'final'
                    observation.code = {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "85354-9",
                            "display": "Blood pressure panel with all children optional"
                        }]
                    }
                    observation.subject = {"reference": f"Patient/{patient.id}"}
                    observation.component = [
                        {
                            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
                            "valueQuantity": {"value": float(systolic), "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}
                        },
                        {
                            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]},
                            "valueQuantity": {"value": float(diastolic), "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}
                        }
                    ]
                    observation.effectiveDateTime = datetime.utcnow().isoformat()
                    bundle_entries.append(BundleEntry(resource=observation, request={'method': 'POST', 'url': 'Observation'}))
                except ValueError:
                    logger.warning(f"Invalid blood pressure format: {bp_raw}")

            bundle = Bundle.model_construct()
            bundle.type = 'transaction'
            bundle.entry = bundle_entries
            
            return bundle.model_dump_json()
            
        except Exception as e:
            logger.error(f"Error mapping data: {e}")
            raise ValueError(f"Mapping failed: {str(e)}")
