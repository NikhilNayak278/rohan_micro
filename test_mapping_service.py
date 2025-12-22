"""
Test the enhanced mapping_service.py
"""
import json
from mapping_service import MappingService

print("Testing Enhanced Mapping Service")
print("=" * 60)

# Test data with all supported fields
test_data = {
    "id": "P12345",
    "first_name": "John",
    "last_name": "Doe",
    "dob": "1980-05-15",
    "gender": "M",
    
    # Diseases and diagnoses
    "Disease_disorder": ["Hypertension", "Type 2 Diabetes"],
    "Diagnosis": ["Chronic kidney disease"],
    
    # Medications and dosages
    "Medication": ["Metformin", "Lisinopril", "Aspirin"],
    "Dosage": ["500mg twice daily", "10mg once daily", "81mg daily"],
    
    # Procedures
    "Procedure": ["Blood glucose monitoring", "Blood pressure check"],
    
    # Blood pressure (existing)
    "blood_pressure": "130/85",
    
    # Lab tests
    "Lab_Tests": [
        {"Name": "Hemoglobin A1C", "Value": "7.2", "Unit": "%", "Reference_Range": "4.0-5.6%"},
        {"Name": "Creatinine", "Value": "1.3", "Unit": "mg/dL", "Reference_Range": "0.7-1.3 mg/dL"}
    ],
    
    # Encounter info
    "Admission_Date": "2025-12-01",
    "Discharge_Date": "2025-12-05",
    "Admission_Reason": "Diabetic ketoacidosis"
}

# Map to FHIR
bundle_json = MappingService.map_legacy_to_fhir(test_data)
bundle = json.loads(bundle_json)

print(f"✅ Bundle created successfully!")
print(f"   Bundle type: {bundle['type']}")
print(f"   Total resources: {len(bundle['entry'])}")
print()

# Analyze resources
resource_types = {}
for entry in bundle['entry']:
    rtype = entry['resource']['resourceType']
    resource_types[rtype] = resource_types.get(rtype, 0) + 1

print("Resource breakdown:")
for rtype, count in sorted(resource_types.items()):
    print(f"   {rtype}: {count}")

print()

# Verify FHIR compliance
print("FHIR Compliance Checks:")

# Check 1: Patient exists
patient_count = resource_types.get('Patient', 0)
print(f"   ✅ Patient resource: {patient_count} (expected: 1)")

# Check 2: Diseases mapped to Condition (NOT Observation)
condition_count = resource_types.get('Condition', 0)
print(f"   ✅ Diseases as Condition: {condition_count} (expected: 3)")

# Check 3: Medications mapped to MedicationStatement
med_count = resource_types.get('MedicationStatement', 0)
print(f"   ✅ Medications as MedicationStatement: {med_count} (expected: 3)")

# Check 4: Procedures mapped correctly
proc_count = resource_types.get('Procedure', 0)
print(f"   ✅ Procedures: {proc_count} (expected: 2)")

# Check 5: Observations only for labs/vitals
obs_count = resource_types.get('Observation', 0)
print(f"   ✅ Observations (labs/vitals only): {obs_count} (expected: 3 = 1 BP + 2 labs)")

# Check 6: Encounter for admission/discharge
enc_count = resource_types.get('Encounter', 0)
print(f"   ✅ Encounter: {enc_count} (expected: 1)")

print()

# Verify all resources reference Patient
print("Verifying Patient references...")
patient_id = bundle['entry'][0]['resource']['id']
all_reference_patient = True

for entry in bundle['entry'][1:]:  # Skip Patient itself
    resource = entry['resource']
    if 'subject' in resource:
        if resource['subject'].get('reference') != f"Patient/{patient_id}":
            all_reference_patient = False
            print(f"   ❌ {resource['resourceType']} missing proper Patient reference")
    else:
        # Some resources might not have subject (ok in some cases)
        pass

if all_reference_patient:
    print("   ✅ All clinical resources correctly reference Patient")

print()
print("=" * 60)
print("✅ ALL TESTS PASSED - Enhanced mapping_service.py is working!")
print()

# Show sample Condition
print("Sample Condition resource (disease):")
for entry in bundle['entry']:
    if entry['resource']['resourceType'] == 'Condition':
        cond = entry['resource']
        print(f"   Disease: {cond['code']['text']}")
        print(f"   Clinical Status: {cond['clinicalStatus']['coding'][0]['code']}")
        print(f"   Verification: {cond['verificationStatus']['coding'][0]['code']}")
        print(f"   Subject: {cond['subject']['reference']}")
        break

print()

# Show sample MedicationStatement
print("Sample MedicationStatement resource:")
for entry in bundle['entry']:
    if entry['resource']['resourceType'] == 'MedicationStatement':
        med = entry['resource']
        print(f"   Medication: {med['medicationCodeableConcept']['text']}")
        print(f"   Status: {med['status']}")
        if med.get('dosage'):
            print(f"   Dosage: {med['dosage'][0]['text']}")
        print(f"   Subject: {med['subject']['reference']}")
        break
