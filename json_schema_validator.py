import json
import yaml
import argparse

from jsonschema import validate, exceptions
from jsonschema.validators import Draft7Validator

def load_schema(category):
    with open("json_schemas/schemas/"+category+"_schema.json", "r") as f:
        schema = json.load(f)

    return schema

def load_input_file(input_file_name):
    with open("json_schemas/schema_tests/"+input_file_name, "r") as f:
        # print(f"Here is filename: {'json_schemas/schema_tests/'+input_file_name}")
        instance = json.load(f)

    return instance

with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

parser = argparse.ArgumentParser(description='Run the validator.')
parser.add_argument('-c', '--category',
                    choices=['contributors',
                    'dataset',
                    'funders',
                    'image',
                    'instrument',
                    'publication',
                    'record',
                    'specimen'],
                    default=cfg['category'],
                    help='Metadata category to validate')
parser.add_argument('-i', '--input_file_name',
                    default=cfg['input_file_name'],
                    help='Tell which input data file to validate.')


args = parser.parse_args()
input_category = args.category.capitalize()
input_file_name = args.input_file_name

instance = load_input_file(input_file_name)
schema = load_schema(input_category)

categories_dict = {
    "Contributors": [ "datasetID", "contributorName", "Creator", "contributorType", "nameType", "nameIdentifier", "nameIdentifierScheme", "affiliation", "affiliationIdentifier", "affiliationIdentifierScheme" ],
    "Dataset": [ "datasetID", "Title", "socialMedia", "Subject", "subjectScheme", "Rights", "rightsURI", "rightsIdentifier", "Image", "generalModality", "generalModalityOther", "Technique", "techniqueOther", "Abstract", "Methods", "technicalInfo" ],
    "Funders": [ "datasetID", "funderName", "fundingReferenceIdentifier", "fundingReferenceIdentifierType", "awardNumber", "awardTitle" ],
    "Image": [ "datasetID", "xAxis", "obliqueXDim1", "obliqueXDim2", "obliqueXDim3", "yAxis", "obliqueYDim1", "obliqueYDim2", "obliqueYDim3", "zAxis", "obliqueZDim1", "obliqueZDim2", "obliqueZDim3", "landmarkName", "landmarkX", "landmarkY", "landmarkZ", "Number", "displayColor", "Representation", "Flurophore", "stepSizeX", "stepSizeY", "stepSizeZ", "stepSizeT", "Channel", "Slices", "t", "xSize", "ySize", "zSize", "Gbyte", "File", "dimensionOrder" ],
    "Instrument": [ "datasetID", "microscopeType", "microscopeManufacturerAndModel", "objectiveManufacturerAndModel", "objectiveImmersion", "objectiveNA", "objectiveMagnification", "detectorType", "detectorManufacturerAndModel", "illuminationType", "illuminationWavelength", "detectionWavelength", "sampleTemperature" ],
    "Publications": [ "datasetID", "relatedIdentifier", "relatedIdentifierType", "PMCID", "relationType", "Citation" ],
    "Specimen": [ "datasetID", "localID", "Species", "NCBITaxonomy", "Age", "ageUnit", "Sex", "Genotype", "organLocalID", "organName", "sampleLocalID", "Atlas", "Location" ]
}

print(f'\nValidating submitted instance for category: "{input_category}"...')

try:
    validate(instance=instance, schema=schema)
    print('No errors found')
except exceptions.ValidationError:
    v = Draft7Validator(schema)
    error_list = sorted(v.iter_errors(instance), key=str)
    print(f"Validation error(s) found: {len(error_list)}")
    i = 1
    for error in error_list:
        if input_category == "Record":
            category = list(set(error.schema_path).intersection(list(categories_dict.keys())))[0]
        else:
            category = input_category
        property = list(set(error.schema_path).intersection(categories_dict[category]))
        if len(property) == 0:
            property = "missing"
        print(f"\nError {i}:")
        print(f"Category: {''.join(category)}")        
        print(f"Property: {''.join(property)}")
        print(error.message)
        i += 1
