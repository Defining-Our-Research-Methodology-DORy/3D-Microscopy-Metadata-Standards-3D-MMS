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
        print(f"Here is filename: {'json_schemas/schema_tests/'+input_file_name}")
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
category = args.category
input_file_name = args.input_file_name

instance = load_input_file(input_file_name)
schema = load_schema(category)

print(f'Validating submitted instance for category: "{category}"...')

try:
    validate(instance=instance, schema=schema)
    print('No errors found')
except exceptions.ValidationError:
    v = Draft7Validator(schema)
    tree = exceptions.ErrorTree(v.iter_errors(instance))
    error_list = sorted(v.iter_errors(instance), key=str)
    print(f"Validation error(s) found: {len(error_list)}")
    for error in error_list:
        print(error.message)
