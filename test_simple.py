from mapping_service import MappingService
import json

# Simple test
data = {
    'id': 'T1',
    'first_name': 'Test',
    'last_name': 'User',
    'Disease_disorder': ['Diabetes']
}

result = MappingService.map_legacy_to_fhir(data)
bundle = json.loads(result)
print(f"Bundle entries: {len(bundle['entry'])}")
print(f"Resource types: {[e['resource']['resourceType'] for e in bundle['entry']]}")
print("Success!")
