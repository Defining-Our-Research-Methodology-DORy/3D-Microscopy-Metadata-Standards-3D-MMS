# Essential Metadata for 3D Brain Microscopy - JSON Validation

## Overview
The Essential Metadata for 3D BRAIN Microscopy, developed by the [BRAIN 3D Microscopy Working Group](https://doryworkspace.org/WorkingGroupRoster), helps ensure that a 3D microscopy dataset is sufficiently described to support its’ re-use by scientists who did not generate the data. Adoption of these metadata standards will aid investigators who want to share data, helping them to evaluate and decide which data can be combined.

The metadata fields are organized into seven categories: Contributors, Funders, Publication, Instrument, Dataset, Specimen, and Image.  Each metadata field is specified by a name, definition, a list of allowable values, whether it is required, and the number of times it can be repeated for a dataset.  The tables for each metadata field can be found at the DORY Workspace site linked below:

https://doryworkspace.org/metadata

## Funding
The research was supported by the National Institute Of Mental Health of the National Institute of Health under Award Number R24MH114683. The content is solely the responsibility of the authors and does not necessarily represent the official views of the National Institutes of Health.

## Branch status
The main branch is at version 1.0, as of November 19, 2021.

## Validator usage
The JSON Validator takes in a user's submitted data in JSON form and compares its contents to the specifications of the corresponding categorical JSON schema, returning a message indicating if any errors found and along with details of found errors.

### Purpose
The validator can be used to confirm submitted data, whether a full dataset or individual category, meets the submission criteria found for each category found on the DORY website.

### Configuration
Configuration options to specify input file name and category are available in `config.yaml`.

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
