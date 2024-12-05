import csv
import json
import re


files = ['M365.json', 'Azure.json']
az_pattern = r"(?<=\n)az[^\n]+(?=\n)"
int_pattern = r"\d+\."

def main():
    merge()
    enrich()


'''Merges the M365.json and Azure.json made with the json_cis_pdf_parser.py'''
def merge():
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
                        #value = re.sub(r'([.!?])', r'\1\n', value)



        result.extend(jsonData)

    with open('output.json', 'w') as fo:
        json.dump(result, fo)


'''The todo's to link the CIS item to the To Do'''
def enrich():
    lookup = dict()
    result = list()

    with open('TODO.csv', newline='') as fc:
        reader = csv.DictReader(fc, delimiter=',')
        for row in reader:
            lookup[row["Source Number"]] = row.get("Check Number", "")  

    with open ('output.json', 'r') as fi:
        cisItems = json.load(fi)
        for item in cisItems:
            check = lookup.get(item["Rule_number"], "")
            for source,check in lookup.items():
                if source == item["Rule_number"]:
                    if check.startswith("A") and item["pdf"] == "azure":
                        item["Check_number"] = check 
                        result.append(item)
                    elif check.startswith("M") and item["pdf"] == "m365":
                        item["Check_number"] = check 
                        result.append(item)

    with open('results.json', 'w+') as fw:
        fw.write(json.dumps(result))


main()