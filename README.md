# Essential Metadata for 3D Brain Microscopy - JSON Validation

## Overview
The Essential Metadata for 3D BRAIN Microscopy, developed by the [BRAIN 3D Microscopy Working Group](https://doryworkspace.org/WorkingGroupRoster), helps ensure that a 3D microscopy dataset is sufficiently described to support its’ re-use by scientists who did not generate the data. Adoption of these metadata standards will aid investigators who want to share data, helping them to evaluate and decide which data can be combined.

The metadata fields are organized into seven categories: Contributors, Funders, Publication, Instrument, Dataset, Specimen, and Image.  Each metadata field is specified by a name, definition, a list of allowable values, whether it is required, and the number of times it can be repeated for a dataset.  The tables for each metadata field can be found at the DORY Workspace site linked below:

https://doryworkspace.org/metadata

## Funding
The research was supported by the National Institute Of Mental Health of the National Institute of Health under Award Number R24MH114683. The content is solely the responsibility of the authors and does not necessarily represent the official views of the National Institutes of Health.

## Branch status
The main branch is at version 1.0, as of November 19, 2021.

## Initialization

### Python set up
This code was written in Python (versions 3.6.8 and above).  The list of required Python packages is provided in `requirements.txt` and can be used to initialize an environment of the user's choice.

### Configuration file
A `config.yaml` file is provided where a user can specify input files and categories for the Data Conversion and Validator scripts.  Parameters corresponding to each script are as follows:

`convert_and_extract_from_csv.py`
- input_excel_file: specifies which Excel workbook to use

`json_schema_validator.py`
- category: specifies which metadata category to validate against
- input_file_name: specifies which input JSON file to validate

Input files should be placed in the directory `json_schemas/input_files`.

## BRAIN Image Data Input
To add BRAIN image data, use the following steps:
- navigate to `json_schemas/input_files`
- make a copy of the Excel file `microscopy_metadata_entry_template.xlsm` and rename to something else
- change the `input_excel_file` parameter above to this new name
- open the new Excel file and follow instructions in the `README` sheet

## Data Conversion and Validation usage

### Purpose
The conversion script is used to convert input BRAIN datasets in Excel form to a JSON format, which is then run through a JSON Schema validator to confirm that the data meets criteria found on the DORY website.  After converting the BRAIN datasets from Excel to JSON formats, the validator will check the newly generated JSON file against pre-defined JSON schemas.  Any resulting discrepancies or errors will be displayed on the command line terminal.

### Usage
To run the conversion script, from the main directory, run the following in the command line.

```
python convert_and_extract_from_csv.py
```

This will use the configuration found in `config.yaml`.  To specify a different input excel file from the command line, use the `-i` argument, as detailed in the Command Line Options section.  An example of specifying from the command line for a different Excel sheet, named "example_metadata_file_here.xlsx", is below.

```
python convert_and_extract_from_csv.py -i example_metadata_file_here.xlsx
```

```
usage: convert_and_extract_from_csv.py [-h] [-i INPUT_EXCEL_FILE]

Run the conversion script.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_EXCEL_FILE, --input_excel_file INPUT_EXCEL_FILE       
                        Tell which input Excel file to convert. 
```

## Validator usage
The JSON Validator takes in a user's submitted data in JSON form and compares its contents to the specifications of the corresponding categorical JSON schema, returning a message indicating if any errors found and along with details of found errors.

### Purpose
The validator can be used to confirm submitted data, whether a full dataset or individual category, meets the submission criteria found for each category found on the DORY website.

### Usage
To run the validator, from the main directory, run the following in the command line.

```
python json_schema_test.py
```

This will use the configuration found in `config.yaml`.  To specify a different input file or category from the command line, use the `-i` or `-c` arguments, respectively, as detailed in the Command Line Options section.  An example of specifying from the command line for the category `funders` is below.

```
python json_schema_validator.py -c funders -i funders_test.json
```

```
usage: json_schema_test.py [-h] [-i INPUT_FILE_NAME]
                           [-c {contributors,dataset,funders,image,instrument,publication,record,specimen}]

Run the annotators.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE_NAME, --input_file_name INPUT_FILE_NAME
                        Tell which input data file to validate.
  -c {contributors,dataset,funders,image,instrument,publication,record,specimen}, --category {contributors,dataset,funders,image,instrument,publication,record,specimen}
                        Metadata category to validate
```
