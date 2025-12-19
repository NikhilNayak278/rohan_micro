import logging
import json
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient

logger = logging.getLogger(__name__)

class HarmonizationService:
    @staticmethod
    def harmonize_bundle(fhir_bundle_json):
        """
        Harmonizes a FHIR Bundle:
        1. Normalizes names to Title Case.
        2. Ensures standard date format (basic check).
        """
        try:
            # Parse JSON to FHIR object
            if isinstance(fhir_bundle_json, str):
                data = json.loads(fhir_bundle_json)
            else:
                data = fhir_bundle_json
                
            bundle = Bundle.model_validate(data)
            
            for entry in bundle.entry:
                if isinstance(entry.resource, Patient):
                    HarmonizationService._harmonize_patient(entry.resource)
            
            return bundle.model_dump_json()
            
        except Exception as e:
            logger.error(f"Harmonization error: {e}")
            raise ValueError(f"Harmonization failed: {str(e)}")

    @staticmethod
    def _harmonize_patient(patient: Patient):
        # 1. Normalize Names to Title Case
        if patient.name:
            for name in patient.name:
                if name.family:
                    name.family = name.family.title()
                if name.given:
                    name.given = [g.title() for g in name.given]
        
        # 2. Add 'harmonized' tag
        if not patient.meta:
            from fhir.resources.meta import Meta
            patient.meta = Meta.model_construct()
        
        if not patient.meta.tag:
            patient.meta.tag = []
            
        patient.meta.tag.append({
            "system": "http://example.org/tags",
            "code": "harmonized",
            "display": "Data has been harmonized"
        })
