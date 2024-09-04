import csv
import json

test = {}
test2 = []
test3 = {}

with open('TODO.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        test[row["Source Number"]] = row.get("Check Number", "")  

with open ('cis.json', 'r') as jsonfile:
    d = json.load(jsonfile)
    for x in d:
        check = test.get(x["Rule_number"], "")
        for source,check in test.items():
            if source == x["Rule_number"]:
                x["Check_number"] = check 
                test2.append(x)

with open('results.json', 'w+') as jsonwrite:
    jsonwrite.write(json.dumps(test2))
