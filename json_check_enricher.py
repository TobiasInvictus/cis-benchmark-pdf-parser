import csv
import json
import os.path


files = ['M365.json', 'Azure.json']
export_file = 'results.json'
az_pattern = r"(?<=\n)az[^\n]+(?=\n)"
int_pattern = r"\d+\."

def main():
    detected = detect()
    merge()
    enrich(detected)


def detect():
    '''Check the current state of the file, and only add what's not already there'''
    checks = list()

    if os.path.isfile(export_file):
        with open(export_file, 'r') as fd:
            resultData = json.load(fd)
            for result in resultData:
                checks.append(result['Check_number'])
        return checks
    else:
        '''Move on to create the file'''
        return checks


def merge():
    '''Merges the M365.json and Azure.json made with the json_cis_pdf_parser.py'''
    result = list()

    for file in files:
        with open(file, 'r') as fi:
            jsonData = json.load(fi)
               
        for line in jsonData: 
            if file == "M365.json":
                line.update({'pdf': 'm365'})
            elif file == "Azure.json":
                line.update({'pdf': 'azure'})
            else:
                exit
            
            '''This little gem does some match replace to fix how the dict ends up looking'''
            for key, value in line.items():
                if type(value) is dict:
                    for k, v in value.items():
                        value[k] = (v.replace(": \n1", "1").replace(": 1", "1").replace("\n1. ", "1.").replace(": \n", "").replace("\no \n", "").replace(" > \n", " > ").replace("\u2022 \n", "\n\u2022 \n").replace("\n\n\u2022 \n","\n\u2022"))
                elif type(value) is str:
                    pass

        result.extend(jsonData)

    with open('output.json', 'w') as fo:
        json.dump(result, fo)


def enrich(detected):
    """The todo's to link the CIS item to the To Do."""
    lookup = {}

    # Load the TODO mapping
    with open('TODO.csv', newline='') as fc:
        reader = csv.DictReader(fc, delimiter=',')
        for row in reader:
            lookup[row["Source Number"]] = row.get("Check Number", "")

    # Load existing results from export_file
    if os.path.isfile(export_file):
        with open(export_file, 'r') as fw:
            try:
                existing_data = json.load(fw)  # Load existing data
            except json.JSONDecodeError:
                print(f"Error reading {export_file}: Starting with an empty result.")
                existing_data = []
    else:
        existing_data = []

    # Convert existing data to a set of Check_number for quick lookups
    existing_check_numbers = {item.get("Check_number") for item in existing_data}

    # Prepare new items to add
    new_items = []
    with open('output.json', 'r') as fi:
        cis_items = json.load(fi)
        for item in cis_items:
            check = lookup.get(item["Rule_number"], "")
            if check and check not in detected and check not in existing_check_numbers and check != "":
                if check.startswith("A") and item["pdf"] == "azure":
                    print(f"Adding {check}")
                    item["Check_number"] = check
                    new_items.append(item)
                elif check.startswith("M") and item["pdf"] == "m365":
                    print(f"Adding {check}")
                    item["Check_number"] = check
                    new_items.append(item)
            else:
                if check != "":
                    print(f"Check {check} already in the JSON")

    # Merge existing data with new items
    updated_data = existing_data + new_items

    # Write back the updated JSON
    with open(export_file, 'w') as fw:
        json.dump(updated_data, fw, indent=4)

    print(f"Enrichment completed. {len(new_items)} new items added.")


    with open(export_file, 'w') as fw:
        json.dump(updated_data, fw, indent=4)


main()