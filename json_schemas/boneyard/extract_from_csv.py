import pandas as pd
import regex as re
import json

# Read in component csv files and convert to a record in dictionary format

record = {}

# =========== List Components =============
list_record_components = ['Contributors', 'Publication', 'Funders'] # components that allow multiple entries (multiple contributors, funders, etc.)

for c in list_record_components:
    df = pd.read_csv(f"input_files/BIL_DOI_datasets_MM_{c.lower()}.csv", keep_default_na=False)
    object_list = [] # keeps track of record entries

    arrayCols = [re.search('^[a-zA-Z]*', x)[0] for x in df.columns if re.search('array$', x)] # identify columns which are arrays (can have multiple values)
    df.columns = [re.search('^[a-zA-Z]*', x)[0] for x in df.columns] # clean up column names

    id_col = [col for col in df.columns if (re.search('Name$', col) or re.search('relatedIdentifier$', col))] # identify the unique id column if there is one
    if len(id_col) == 1:
        id_col = id_col[0]
    else:
        id_col = None
    used_ids = {} # keeps tracked of existing unique identifiers
    id_index = 0 # keeps track of the number of unique identifiers

    # create a dict for each row (entry) in the df and add it to a list
    for i in range(len(df)): # Go through rows in dataframe
        record_dict = df.iloc[i].to_dict() # current row represented as a dictionary

        if id_col is not None and record_dict[id_col] in used_ids.keys(): # If there is an id_col that has not already been used
            # Append information in the array columns to an existing entry
            for col in arrayCols:
                if record_dict[col] not in object_list[used_ids[record_dict[id_col]]][col]:
                    object_list[used_ids[record_dict[id_col]]][col].append(record_dict[col])
        else:
            for col in arrayCols: # convert arrayCols to arrays
                record_dict[col] = [record_dict[col]]

            object_list.append(record_dict) # append row to the object list as a new entry
            if id_col is not None: # add id to used_ids
                used_ids[record_dict[id_col]] = id_index
                id_index += 1
    record[c] = object_list


# =========== Object Components =============
object_record_components = ['Instrument', 'Dataset', "Specimen", "Image"] # components that do not allow multiple entries (instrument, etc.)

for c in object_record_components:
    df = pd.read_csv(f"input_files/BIL_DOI_datasets_MM_{c.lower()}.csv", keep_default_na=False)

    # clean up column names and add row to the record
    df.columns = [re.search('^\w*', x)[0] for x in df.columns]
    record[c] = df.iloc[0].to_dict()

with open("output_files/BIL_DOI_datasets_MM.json", "w") as f:
    json.dump(record, f)
