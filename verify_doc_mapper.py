import logging
import json
import uuid
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fhir.resources.condition import Condition
from harmon_service.document_mapper import DocumentMapper, MedicalReportMapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_document_mapper():
    logger.info("Verifying DocumentMapper Terminology Integration...")

    # Instantiate a mapper (using MedicalReportMapper since DocumentMapper is abstract)
    mapper = MedicalReportMapper()
    mapper.patient_id = str(uuid.uuid4())

    # Test Case 1: Known Disease (Hypertension)
    logger.info("Test Case 1: Looking up 'Hypertension'...")
    condition_htn = mapper._build_condition("Hypertension")
    
    # Verify structure
    if condition_htn.code.coding:
        # coding[0] might be a dict if model_construct was used non-recursively
        code_entry = condition_htn.code.coding[0]
        # Handle both dict and object for robustness in test
        code_val = code_entry.get('code') if isinstance(code_entry, dict) else code_entry.code
        display_val = code_entry.get('display') if isinstance(code_entry, dict) else code_entry.display
        system_val = code_entry.get('system') if isinstance(code_entry, dict) else code_entry.system
        
        logger.info(f"Success! Found code: {code_val} ({display_val})")
        if system_val == "http://hl7.org/fhir/sid/icd-10-cm":
             logger.info("System matches ICD-10 CM.")
        else:
             logger.error(f"Unexpected system: {system_val}")
    else:
        logger.error("Failed to find coding for Hypertension.")

    # Test Case 2: Unknown/Garbage Text (Fallback Check)
    garbage_text = "SuperRareConditionXYZ123"
    logger.info(f"Test Case 2: Looking up '{garbage_text}' (expecting fallback)...")
    condition_garbage = mapper._build_condition(garbage_text)
    
    if not condition_garbage.code.coding and condition_garbage.code.text == garbage_text:
        logger.info("Success! Fallback worked correctly (text only, no coding).")
    else:
        logger.error(f"Fallback check failed. Result: {condition_garbage.json()}")

    logger.info("DocumentMapper Verification Complete.")

if __name__ == "__main__":
    verify_document_mapper()
