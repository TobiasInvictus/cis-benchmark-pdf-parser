import csv
import json

test = {}
test2 = []

"""
Parses the TODO.csv file in order to apply the right checkname:cis id mapping, outputs to a new jsonfile
""" 

with open('TODO.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        test[row["Source Number"]] = row.get("Check Number", "")  

with open ('output.json', 'r') as jsonfile:
    d = json.load(jsonfile)
    for x in d:
        check = test.get(x["Rule Number"], "")
        for source,check in test.items():
            if source == x["Rule Number"]:
                x["Check Number"] = check 
                test2.append(x)

with open('information.json', 'w+') as jsonwrite:
    jsonwrite.write(json.dumps(test2))
