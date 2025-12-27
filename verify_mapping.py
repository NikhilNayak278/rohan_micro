
import logging
import json
import sys
import unittest
from datetime import datetime

# Add the parent directory to sys.path to ensure modules can be imported
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from harmon_service.mapping_service import MappingService
from harmon_service.terminology import get_condition_code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMappingService(unittest.TestCase):
    def test_terminology_service(self):
        """Test the terminology service separately."""
        logger.info("Testing Terminology Service...")
        
        # Test known disease
        result_htn = get_condition_code("Hypertension")
        self.assertIn("coding", result_htn)
        self.assertEqual(result_htn["text"], "Hypertension")
        logger.info(f"Hypertension Result: {result_htn}")
        
        # Test cache (second call should be fast/cached)
        start_time = datetime.now()
        get_condition_code("Hypertension")
        duration = datetime.now() - start_time
        logger.info(f"Cache hit duration: {duration}")

        # Test empty/fallback
        result_empty = get_condition_code("")
        self.assertEqual(result_empty["text"], "")
        
        result_garbage = get_condition_code("kajsdfhaksjdhfiuqwhef")
        # Should fallback to text only
        self.assertEqual(result_garbage["text"], "kajsdfhaksjdhfiuqwhef")
        logger.info("Terminology Service Test Passed")

    def test_mapping_service_robustness(self):
        """Test MappingService with mixed valid and invalid data."""
        logger.info("Testing Mapping Service Robustness...")
        
        legacy_data = {
            "id": "123",
            "first_name": "Test",
            "last_name": "Patient",
            "dob": "1990-01-01",
            "gender": "M",
            "Disease_disorder": ["Hypertension", "InvalidDiseaseThatMightFailAPI", None, ""], # Mixed list
            "Diagnosis": "Diabetes", # String instead of list
            "Medication": ["Metformin", "BadMed", ""],
            "Dosage": ["500mg", None], # Mismatched length implicitly
            "Lab_Tests": [
                {"Name": "Hemoglobin", "Value": "14.5", "Unit": "g/dL"},
                {"Name": "BrokenTest", "Value": "NotANumber", "Unit": "N/A"}, # Should handle value error gracefully
                "InvalidStringEntry" # Should not crash
            ]
        }
        
        try:
            bundle_json = MappingService.map_legacy_to_fhir(legacy_data)
            bundle = json.loads(bundle_json)
            
            logger.info(f"Generated Bundle Entry Count: {len(bundle.get('entry', []))}")
            
            # Verify Patient Exists
            patient_entry = next((e for e in bundle['entry'] if e['resource']['resourceType'] == 'Patient'), None)
            self.assertIsNotNone(patient_entry)
            
            # Verify Conditions (Hypertension + Diabetes should be there)
            conditions = [e for e in bundle['entry'] if e['resource']['resourceType'] == 'Condition']
            self.assertTrue(len(conditions) >= 2)
            
            # Verify Medications (Metformin should be there)
            meds = [e for e in bundle['entry'] if e['resource']['resourceType'] == 'MedicationStatement']
            self.assertTrue(len(meds) >= 1)
            # Check for RxNorm
            metformin_med = next((m for m in meds if "Metformin" in json.dumps(m)), None)
            if metformin_med:
                med_cc = metformin_med['resource'].get('medicationCodeableConcept', {})
                self.assertTrue(any(c.get('system') == "http://www.nlm.nih.gov/research/umls/rxnorm" for c in med_cc.get('coding', [])))
            
            # Verify Labs (Hemoglobin should have LOINC)
            observations = [e for e in bundle['entry'] if e['resource']['resourceType'] == 'Observation']
            hemo_obs = next((o for o in observations if o['resource'].get('code', {}).get('text') == "Hemoglobin"), None)
            if hemo_obs:
                self.assertTrue(any(c.get('system') == "http://loinc.org" for c in hemo_obs['resource']['code'].get('coding', [])))

            logger.info("Mapping Service Robustness Test Passed")
            
        except Exception as e:
            self.fail(f"Mapping Service crashed with error: {e}")

if __name__ == '__main__':
    unittest.main()
