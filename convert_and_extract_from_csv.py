import regex as re
import json
import numpy as np
import pandas as pd
import os
import yaml
import argparse
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
from jsonschema import validate, exceptions
from jsonschema.validators import Draft7Validator

# ========================================== Script Information ===========================================
'''
This script takes an input data entry excel file containing metadata for the BRAIN project and splits it into individual 
csv files for each metadata group (Contributors, Funders, etc.). The individual csv files are then parsed and converted
into a dictionary representation of the metadata record which is then written to a json file. The json file can be
validated against record_schema.json.
Data entry file: brain-metadata-validation/json_schemas/input_files/3D_brain_microscopy_metadata_entry_template.xlsm 
'''
# ========================================== Functions ===========================================
def split_csv(val):
    """
    Split a string by parentheses or commas
    :param val (str, req): string value to be split
    :return: input string split into a list
    """
    p = "\([^\)\(]*\)"  # matches sets of parentheses
    if type(val) != str:
        return val
    matches = re.findall(p, val) # find all sets of parentheses
    num_matches = len(matches)

    if num_matches == 0: # if there are no parentheses, split using a ","
        split_val = val.split(',')
    elif num_matches == 1: # if there is one set of parentheses, remove the parentheses and split using a ","
        split_val = val[1:-1].split(',')
    elif num_matches > 1: # if there are multiple sets of parentheses, split on the parentheses
        split_val = list(matches)

    for j, k in enumerate(split_val): # for each element in split_val
        try:
            split_val[j] = float(k) # try to convert to a float
        except:
            split_val[j] = split_val[j].strip() # if you can't convert to a float strip white space from the string
    return split_val

def extract_csvs(input_excel_file, datestamp):
    """
    Save the input excel file as csv files, with a separate csv file for each group. The current date is added to
    the filenames and files are saved in a directory name being the current date.
    :param input_excel_file: excel file to extract metadata from
    :return: None
    """

    sheet_names = ['Contributors', 'Publications', 'Funders', 'Instrument', 'Dataset', "Specimen", "Image", "README", "dropdown"]
    excel_dict = pd.read_excel(input_excel_file, sheet_name=None, skiprows=2, engine="openpyxl")
    path = f"json_schemas/output_files/{datestamp}"

    if not os.path.exists(path):
        os.makedirs(path)

    if not all(e in excel_dict.keys() for e in sheet_names):
        missing_sheets = [e for e in sheet_names if e not in excel_dict.keys()]
        raise Exception(f"{' and '.join(missing_sheets)} category/categories were expected but is/are missing.")
    for sheet in excel_dict.keys():
        if sheet == "README" or sheet == "dropdown":
            continue
        elif sheet not in sheet_names:
            raise Exception(f"{sheet} is not a known metadata category.")
        else:
            output_file = f'{path}/{sheet.lower()}_{datestamp}.csv'
            with open(output_file, 'w+', encoding="utf-8") as f:
                output_df = excel_dict[sheet]
                output_df.drop(output_df.filter(regex="Unname"),axis=1, inplace=True)
                output_df = output_df[output_df['datasetID*'].notna()]
                output_df.to_csv(f, index=False)


def add_new_datasets(metadata_record, dataset_ids, metadata_components):
    """
    Add a new dataset to the record dict for each dataset_id.
    :param metadata_record: metadata record to be added to
    :param dataset_ids: list of dataset_ids in the csv file
    :param metadata_components: list of columns (information fields) in the csv file
    :return: metadata_record dictionary
    """
    for id in dataset_ids:
        if id in metadata_record.keys():
            pass
        else:
            metadata_record[id] = {}
            for c in metadata_components:
                metadata_record[id][c] = []
    return metadata_record

def parse_row(df, i, group_id_col, csvCols):
    '''
    Go through a single row in a csv file and parse the information into a dictionary. Also, get the
    dataset_id and group_id for the row
    :param df: dataframe to be parsed
    :param i: row to be parsed
    :param group_id_col: column name for the unique identifier for the group
    :param csvCols: list of columns that can contain multiple values
    :return: dictionary with information from the row (row_dict) as well as the dataset and group ids
    '''
    row_dict = df.iloc[i].to_dict()  # current row represented as a dictionary
    dataset_id = row_dict['datasetID']

    # Set group id if there is one
    if group_id_col is not None:
        group_id = row_dict[group_id_col]
    else:
        group_id = None

    # Format data in row_dict
    for col in df.columns:
        try:
            row_dict[col] = float(row_dict[col]) # Convert fields to float if possible
        except:
            pass

        # convert NaNs to None
        if type(row_dict[col]) not in [str, list] and row_dict[col] is not None and np.isnan(
                row_dict[col]):
            row_dict[col] = None

        # Split the values by column if the column is a csv column
        if col in csvCols and row_dict[col] != None:
            split_val = split_csv(row_dict[col])
            row_dict[col] = split_val
        elif col in csvCols and row_dict[col] == None:
            row_dict[col] = []
    return row_dict, dataset_id, group_id

def clean_col_names(df):
    """
    Clean up the dataframe names and identify the csv columns and unique id column if there is one
    :param df: dataframe to be modified
    :return: dataframe with cleaned column names and a list of columns which ae allowed to have multiple values (csvCols)
    """
    csvCols = [x.split('+')[0] for x in df.columns if '+' in x]  # list of columns that can have multiple entries
    df.columns = [re.search('^[a-zA-Z1-9]*', x)[0] for x in df.columns]  # clean up column names
    df.dropna(how="all", inplace=True)
    return df, csvCols

def get_group_id(df):
    """
    Get group ids and dataset ids in the input dataframe
    :param df: input dataframe
    :return: Column name for the group_id and dataset_ids contained in the df
    """
    group_id_rows = [col for col in df.columns if
                     (re.search('[^k]Name$', col) or re.search('relatedIdentifier$', col))]  # identify unique id column
    dataset_ids = list(set(df['datasetID']))

    # Identify the column containing the unique identifier for the metadata group
    if len(group_id_rows) == 1:  # if a unique identifier is found
        group_id_col = group_id_rows[0]
    else:
        group_id_col = None
    return group_id_col, dataset_ids


def parse_group_csv(metadata_record, metadata_group, metadata_groups):
    """
    Parse the csv file for a metadata group (Contributors, Funders, etc.) and return a dictionary containing
    the information in the csv file
    :param metadata_group: Group name for the metadata group being processed
    :param metadata_groups: List of all metadata groups
    :return: dictionary containing the information in the csv file for the specified metadata group
    """
    # Read in component csv file and convert to a metadata_record in dictionary format
    df = pd.read_csv(
        f"json_schemas/output_files/{datestamp}/{metadata_group.lower()}_{datestamp}.csv", encoding="utf-8")
    # metadata_record = {}
    df, csvCols = clean_col_names(df)
    group_id_col, dataset_ids = get_group_id(df)

    metadata_record = add_new_datasets(metadata_record, dataset_ids, metadata_groups)  # create the metadata_record dictionary
    used_ids = {}  # keeps tracked of existing group unique identifiers

    # Create a dict for each row (entry) in the df and add it to a list
    for i in range(len(df)):  # Go through rows in dataframe
        row_dict, dataset_id, group_id = parse_row(df, i, group_id_col, csvCols)

        if group_id is not None:
            # If there is an existing entry for the group_id, go through column by column and append values to the metadata_record dict
            if group_id in used_ids.keys():  # If an entry with the same id already exists
                for col in csvCols:
                    if len(metadata_record[dataset_id][metadata_group]) > 0:
                        metadata_record[dataset_id][metadata_group][used_ids[group_id]][col] += row_dict[col]
                        metadata_record[dataset_id][metadata_group][used_ids[group_id]][col] = list(
                            set(metadata_record[dataset_id][metadata_group][used_ids[group_id]][col]))
            # If there is not entry for group_id, append the entire dictionary to the metadata_record dict
            else:
                if group_id not in used_ids.keys():  # add id to used_ids
                    used_ids[group_id] = i
                    metadata_record[dataset_id][metadata_group].append(row_dict)

        # If there is no unique id column, add the entire row_dict to the metadata_record dict (append or create a new list)
        else:
            try:
                metadata_record[dataset_id][metadata_group].append(row_dict)
            except:
                metadata_record[dataset_id][metadata_group] = [row_dict]

    return metadata_record

def parse_csvs():
    """
    Cycle through the metadata_groups and parse each corresponding csv file into a metadata_record dictionary.
    :return: dictionary with the metadata from all of the groups.
    """
    metadata_groups= ['Contributors', 'Publications', 'Funders', 'Instrument', 'Dataset', "Specimen", "Image"]
    metadata_record = {}
    for c in metadata_groups:
        # metadata_record = parse_group_csv(c, metadata_groups)
        metadata_record = parse_group_csv(metadata_record, c, metadata_groups)
    return metadata_record

def write_json(metadata_record, datestamp):
    """
    Write the metadata record to a json file.
    :param metadata_record: metadata record to be written
    :param datestamp: date stamp to be used in the json file name.
    :return: None
    """
    with open(
            f"json_schemas/output_files/{datestamp}/BIL_DOI_datasets_MM_{datestamp}.json",
            "w") as f:
        json.dump(metadata_record, f)

def read_json(date_stamp):
    """
    Load a json file containing a metadata record dictionary
    :param date_stamp: data stamp for the json file name
    :return: metadata record dictionary from the file
    """
    with open(f"json_schemas/output_files/{date_stamp}/BIL_DOI_datasets_MM_{date_stamp}.json", "r", encoding="utf-8") as f:
        r = json.load(f)
    return r

def load_schema(category):
    with open("json_schemas/schemas/"+category+"_schema.json", "r") as f:
        schema = json.load(f)

    return schema

# =========================== Reading input parameters =======================================
with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

parser = argparse.ArgumentParser(description='Run the conversion script.')
parser.add_argument('-i', '--input_excel_file',
                    default=cfg['input_excel_file'],
                    help='Tell which input Excel file to convert.')

args = parser.parse_args()
input_excel_file = args.input_excel_file

# =========================== Extract csv files from excel template ===========================================
today = pd.to_datetime("today")
datestamp = f'{today.month}{today.day}{today.year}'

# input_excel_file = "json_schemas/input_files/3D_microscopy_metadata_entry_template.xlsm"
input_excel_path = "json_schemas/input_files/" + input_excel_file
extract_csvs(input_excel_path, datestamp)

# =========================== Go through csv files and extract information ==================================
metadata_record = parse_csvs()
write_json(metadata_record, datestamp)

# =========================== Run json validation on metadata record =======================================
schema = load_schema('record')

categories_dict = {
    "Contributors": [ "datasetID", "contributorName", "Creator", "contributorType", "nameType", "nameIdentifier", "nameIdentifierScheme", "affiliation", "affiliationIdentifier", "affiliationIdentifierScheme" ],
    "Dataset": [ "datasetID", "Title", "socialMedia", "Subject", "subjectScheme", "Rights", "rightsURI", "rightsIdentifier", "Image", "generalModality", "generalModalityOther", "Technique", "techniqueOther", "Abstract", "Methods", "technicalInfo" ],
    "Funders": [ "datasetID", "funderName", "fundingReferenceIdentifier", "fundingReferenceIdentifierType", "awardNumber", "awardTitle" ],
    "Image": [ "datasetID", "xAxis", "obliqueXDim1", "obliqueXDim2", "obliqueXDim3", "yAxis", "obliqueYDim1", "obliqueYDim2", "obliqueYDim3", "zAxis", "obliqueZDim1", "obliqueZDim2", "obliqueZDim3", "landmarkName", "landmarkX", "landmarkY", "landmarkZ", "Number", "displayColor", "Representation", "Flurophore", "stepSizeX", "stepSizeY", "stepSizeZ", "stepSizeT", "Channel", "Slices", "t", "xSize", "ySize", "zSize", "Gbyte", "File", "dimensionOrder" ],
    "Instrument": [ "datasetID", "microscopeType", "microscopeManufacturerAndModel", "objectiveManufacturerAndModel", "objectiveImmersion", "objectiveNA", "objectiveMagnification", "detectorType", "detectorManufacturerAndModel", "illuminationType", "illuminationWavelength", "detectionWavelength", "sampleTemperature" ],
    "Publications": [ "datasetID", "relatedIdentifier", "relatedIdentifierType", "PMCID", "relationType", "Citation" ],
    "Specimen": [ "datasetID", "localID", "Species", "NCBITaxonomy", "Age", "ageUnit", "Sex", "Genotype", "organLocalID", "organName", "sampleLocalID", "Atlas", "Location" ]
}

print(f'\nValidating submitted instance for category: "record"...')

try:
    validate(instance=metadata_record, schema=schema)
    print('No errors found')
except exceptions.ValidationError:
    v = Draft7Validator(schema)
    tree = exceptions.ErrorTree(v.iter_errors(metadata_record))
    error_list = sorted(v.iter_errors(metadata_record), key=str)
    print(f"Validation error(s) found: {len(error_list)}")
    i = 1
    for error in error_list:
        category = list(set(error.schema_path).intersection(list(categories_dict.keys())))[0]
        property = list(set(error.schema_path).intersection(categories_dict[category]))
        if len(property) == 0:
            property = "missing"
        print(f"\nError {i}:")
        print(f"Category: {''.join(category)}")        
        print(f"Property: {''.join(property)}")
        print(error.message)
        i += 1