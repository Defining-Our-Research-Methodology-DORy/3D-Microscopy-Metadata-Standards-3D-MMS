import regex as re
import json
import numpy as np

import pandas as pd


def split_csv(val):
    """
    Split the field by parentheses or comma
    :param val: string value to be split
    :return:
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

def extract_csvs(input_excel_file):
    """
    Save the input excel file as csv files, with a separate csv file for each group
    :param input_excel_file:
    :return:
    """
    excel_dict = pd.read_excel(input_excel_file, sheet_name=None, skiprows=2)
    for sheet in excel_dict.keys():
        if sheet == "README" or sheet == "dropdown":
            continue
        else:
            # df[key].to_csv(f'output_files/120321/{key}_120321.csv', index=False)
            output_file = f'brain-metadata-validation/json_schemas/output_files/121421/{sheet.lower()}_121421.csv'
            with open(output_file, 'w+') as f:
                excel_dict[sheet].to_csv(f, index=False)


def add_new_datasets(record, dataset_ids, record_components):
    """
    Add a new dataset to the record dict for each dataset_id.
    :param record: record to be added to
    :param dataset_ids: list of dataset_ids in the csv file
    :param record_components: list of columns (information fields) in the csv file
    :return:
    """
    for id in dataset_ids:
        if id in record.keys():
            pass
        else:
            record[id] = {}
            for c in record_components:
                record[id][c] = []
    return record

# Read in component csv files and convert to a record in dictionary format
record_components = ['Contributors', 'Publications', 'Funders', 'Instrument', 'Dataset', "Specimen", "Image"]

record = {}

# ==================== Go through csv files and extract information ==================================
for c in record_components:

    df = pd.read_csv(f"brain-metadata-validation/json_schemas/output_files/121421/{c.lower()}_121421.csv")

    # clean up the tables and identify the unique id column if there is one
    csvCols = [x.split('+')[0] for x in df.columns if '+' in x] # list of columns that can have multiple entries
    df.columns = [re.search('^[a-zA-Z1-9]*', x)[0] for x in df.columns] # clean up column names
    df.dropna(how="all", inplace=True)
    group_id_rows = [col for col in df.columns if (re.search('[^k]Name$', col) or re.search('relatedIdentifier$', col))] # identify unique id column

    dataset_ids = list(set(df['datasetID']))
    record = add_new_datasets(record, dataset_ids, record_components) # create the record dictionary

    # Set group_id
    if len(group_id_rows) == 1: # if a unique identifier is found
        group_id_col = group_id_rows[0]
    else:
        group_id_col = None
        group_id = None
    used_ids = {} # keeps tracked of existing group unique identifiers

    # Create a dict for each row (entry) in the df and add it to a list
    for i in range(len(df)): # Go through rows in dataframe
        row_dict = df.iloc[i].to_dict() # current row represented as a dictionary
        dataset_id = row_dict['datasetID']

        # Set group id if there is one
        if group_id_col is not None:
            group_id = row_dict[group_id_col]

        # Format data in row_dict
        for col in df.columns:

            # Convert fields to float if possible
            try:
                row_dict[col] = float(row_dict[col])
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


        if group_id is not None:
            # If there is an existing entry for the group_id
            # Go through column by column and append values to the record dict
            if group_id in used_ids.keys():  # If an entry with the same id already exists
                for col in csvCols:
                    record[dataset_id][c][used_ids[group_id]][col] += row_dict[col]
                    record[dataset_id][c][used_ids[group_id]][col] = list(
                        set(record[dataset_id][c][used_ids[group_id]][col]))
            # If there is not entry for group_id
            # Append the entire dictionary to the record dict
            else:
                if group_id not in used_ids.keys():  # add id to used_ids
                    used_ids[group_id] = i
                    record[dataset_id][c].append(row_dict)
        # If there is no unique id column - add the entire row_dict to the record dict (append or create a new list)
        else:
            try:
                record[dataset_id][c].append(row_dict)
            except:
                record[dataset_id][c] = [row_dict]


with open("brain-metadata-validation/json_schemas/output_files/121421/BIL_DOI_datasets_MM_121421.json", "w") as f:
    json.dump(record, f)

with open("output_files/BIL_DOI_datasets_MM_112321_2.json", "r") as f:
    r = json.load(f)

# ============ Extract csv files from excel template ==========
input_excel_file = "brain-metadata-validation/json_schemas/input_files/brain_microscopy_metadata_entry_template.xlsm"