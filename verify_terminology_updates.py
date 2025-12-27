
import logging
import uuid
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fhir.resources.observation import Observation
from fhir.resources.medicationstatement import MedicationStatement
from harmon_service.document_mapper import MedicalReportMapper, LabReportMapper
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_terminology_updates():
    logger.info("Verifying Terminology Updates (LOINC & RxNorm)...")

    # 1. Verify LOINC (Lab Report)
    logger.info("--- Test Case 1: LOINC Lookup (Hemoglobin) ---")
    try:
        lab_mapper = LabReportMapper()
        lab_mapper.patient_id = str(uuid.uuid4())
        
        observation = lab_mapper._build_observation(
            test_name="Hemoglobin",
            value=14.5,
            unit="g/dL"
        )
        
        # Check if code was populated
        coding = observation.code.coding
        if coding:
            code_entry = coding[0]
            # Robust access
            code_val = code_entry.get('code') if isinstance(code_entry, dict) else code_entry.code
            display_val = code_entry.get('display') if isinstance(code_entry, dict) else code_entry.display
            system_val = code_entry.get('system') if isinstance(code_entry, dict) else code_entry.system
            
            logger.info(f"Success! LOINC Code: {code_val} ({display_val})")
            if "loinc.org" in system_val:
                logger.info("System matches LOINC.")
            else:
                logger.error(f"Unexpected system: {system_val}")
        else:
            logger.error("Failed to find LOINC code for Hemoglobin.")
    except Exception as e:
        logger.error(f"Test Case 1 Failed: {e}")
        traceback.print_exc()

    # 2. Verify RxNorm (Medical Report Meds)
    logger.info("--- Test Case 2: RxNorm Lookup (Metformin) ---")
    try:
        med_mapper = MedicalReportMapper()
        med_mapper.patient_id = str(uuid.uuid4())
        
        med_stmt = med_mapper._build_medication_statement(
            medication="Metformin"
        )
        
        # Check medicationCodeableConcept
        # Use proper attribute based on what was set in DocumentMapper
        coding = None
        if med_stmt.medicationCodeableConcept and med_stmt.medicationCodeableConcept.coding:
            coding = med_stmt.medicationCodeableConcept.coding
            
        if coding:
            code_entry = coding[0]
            # Robust access
            code_val = code_entry.get('code') if isinstance(code_entry, dict) else code_entry.code
            display_val = code_entry.get('display') if isinstance(code_entry, dict) else code_entry.display
            system_val = code_entry.get('system') if isinstance(code_entry, dict) else code_entry.system
            
            logger.info(f"Success! RxNorm Code: {code_val} ({display_val})")
            if "rxnorm" in system_val or "umls" in system_val:
                logger.info("System matches RxNorm/UMLS.")
            else:
                logger.error(f"Unexpected system: {system_val}")
        else:
             logger.error("Failed to find RxNorm code for Metformin.")
    except Exception as e:
        logger.error(f"Test Case 2 Failed: {e}")
        traceback.print_exc()

    # 3. Verify Fallback
    logger.info("--- Test Case 3: Invalid Lookup (Fallback) ---")
    obs_fallback = lab_mapper._build_observation(test_name="UnknownTestXYZ", value=10)
    if not obs_fallback.code.coding and obs_fallback.code.text == "UnknownTestXYZ":
        logger.info("Success! Fallback worked (Text only).")
    else:
        logger.error("Fallback failed.")

    logger.info("Terminology Verification Complete.")

if __name__ == "__main__":
    verify_terminology_updates()
