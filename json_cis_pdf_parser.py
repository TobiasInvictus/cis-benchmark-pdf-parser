#!/usr/bin/env python3

import fitz
import json
import re
import logging
import argparse
import sys

def main():
    # Initialize variables
    (
        rule_count,
        level_count,
        description_count,
        acnt,
        rat_count,
        imp_count,
        rem_count,
        defval_count,
        cis_count,
    ) = (0,) * 9
    firstPage = None
    seenList = []

    # Setup console logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging_streamhandler = logging.StreamHandler(stream=None)
    logging_streamhandler.setFormatter(
        logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s")
    )
    logger.addHandler(logging_streamhandler)

    parser = argparse.ArgumentParser(
        description="Parses CIS Benchmark PDF content into JSON Format"
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--pdf_file", type=str, required=True, help="PDF File to parse"
    )
    required.add_argument(
        "--out_file", type=str, required=True, help="Output file in .json format"
    )
    required.add_argument(
        '-l', '--log-level', type=str, required=False, help="Set log level (DEBUG, INFO, etc). Default to INFO",
        default="INFO"
    )
    args = parser.parse_args()

    try:
        logger.setLevel(args.log_level)
    except ValueError:
        logging.error("Invalid log level: {}. Valid log levels can be found here "
                      "https://docs.python.org/3/howto/logging.html".format(args.log_level))
        sys.exit(1)

    # Open PDF File
    doc = fitz.open(args.pdf_file)

    # Get CIS Type from the name of the document in the cover page as it doesn't appear in the metadata
    coverPageText = doc.load_page(0).get_text("text")
    logger.debug(coverPageText)
    try:
        pattern = "(?<=CIS).*(?=Benchmark)"
        rerule = re.search(pattern, coverPageText, re.DOTALL)
        if rerule is not None:
            CISName = rerule.group(0).strip().replace('\n','')
            logger.info("*** Document found name: {} ***".format(CISName))
            if "Red Hat Enterprise Linux 7" in CISName:
                pattern = "(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))"
            elif "Debian Linux 11" in CISName:
                pattern = "(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))"
            elif "Microsoft Windows Server 2019" in CISName:
                pattern = "(\d+(?:\.\d+)+)\s\(((L[12])|(NG))\)(.*?)(\(Automated\)|\(Manual\))"
            elif "Microsoft Windows 10 Enterprise" in CISName:
                pattern = "(\d+(?:\.\d+)+)\s\(((L[12])|(NG)|(BL))\)(.*?)(\(Automated\)|\(Manual\))"
            elif "Microsoft Azure Foundations" in CISName:
                pattern = "(\d+(?:\.\d.\d*)+)(.*?)(\(Automated\)|\(Manual\))"
            else:
                raise ValueError("Could not find a matching regex for {}".format(CISName))
    except IndexError:
        logger.error("*** Could not find CIS Name, exiting. ***")
        exit()

    # Skip to actual rules
    for currentPage in range(len(doc)):
        findPage = doc.load_page(currentPage)
        if findPage.search_for("Recommendations 1 "):
            firstPage = currentPage

    # If no "Recommendations" and "Initial Setup" it is not a full CIS Benchmark .pdf file
    if firstPage is None:
        logger.error("*** Not a CIS PDF Benchmark, exiting. ***")
        exit()

    logger.info("*** Total Number of Pages: %i ***", doc.page_count)

    # Prepare data to be written to JSON
    rules_data = []

    # Loop through all PDF pages
    for page in range(firstPage, len(doc)):
        if page < len(doc):
            data = doc.load_page(page).get_text("text")
            logger.info("*** Parsing Page Number: %i ***", page)

            # Get rule by matching regex pattern for x.x.* (Automated) or (Manual), there are no "x.*" we care about
            try:
                rerule = re.search(pattern, data, re.DOTALL)
                if rerule is not None:
                    rule = rerule.group().replace('\n', '')
                    rulenr = rule.split(" ")[0]
                    rule_count += 1
            except IndexError:
                logger.info("*** Page does not contain a Rule Name ***")
            except AttributeError:
                logger.info("*** Page does not contain a Rule Name ***")

            # Get Profile Applicability by splits as it is always between Profile App. and Description, faster than regex
            try:
                l_post = data.split("Profile Applicability:", 1)[1]
                level = l_post.partition("Description:")[0].strip()
                level = re.sub("[^a-zA-Z0-9\\n-]+", " ", level)
                level_count += 1
            except IndexError:
                logger.info("*** Page does not contain Profile Levels ***")

            # Get Description by splits as it is always between Description and Rationale, faster than regex
            try:
                d_post = data.split("Description:", 1)[1]
                description = d_post.partition("Rationale")[0].strip().replace('\n', '')
                description_count += 1
            except IndexError:
                logger.info("*** Page does not contain Description ***")

            # Get Rationale by splits as it is always between Rationale and Impact, faster than regex
            try:
                rat_post = data.split("Rationale:", 1)[1]
                rat = rat_post.partition("Impact:")[0].strip().replace('\n', '')
                rat_count += 1
            except IndexError:
                logger.info("*** Page does not contain Rationale ***")

            # Get Impact by splits as it is always between Impact and Audit, faster than regex
            try:
                imp_post = data.split("Impact:", 1)[1]
                imp = imp_post.partition("Audit:")[0].strip().replace('\n', '')
                imp_count += 1
            except IndexError:
                logger.info("*** Page does not contain Rationale ***")

            # Get Audit by splits as it is always between Audit and Remediation, faster than regex
            try:
                a_test = {}
                a_post = data.split("\nAudit:", 1)[1]
                audit = a_post.partition("Remediation")[0].strip()
                #audit_steps = list(filter(None, audit.split("From")))
                a_split_results = re.split(r'(From Azure Portal|From REST API|From Powershell|From Azure CLI|From Azure Console|From Azure Policy|From Azure PowerShell)', audit)
                for i in range(1, len(a_split_results), 2):  # Start from index 1 and step by 2 to get delimiters
                    delimiter = a_split_results[i].strip()  # Get the delimiter and remove leading/trailing whitespace
                    string = a_split_results[i + 1].strip()  # Get the corresponding string and remove leading/trailing whitespace
                    a_test.update({delimiter: string}) 
                audit_steps = a_test
                acnt += 1
            except IndexError:
                logger.info("*** Page does not contain Audit ***")

            # Get Remediation by splits as it is always between Remediation and Default value, faster than regex
            try:
                rem_test = {}
                rem_post = data.split("Remediation:", 1)[1]
                rem = rem_post.partition("Default Value:")[0].strip()
                rem_split_results = re.split(r'(From Azure Portal|From REST API|From Powershell|From Azure CLI|From Azure Console|From Azure Policy|From Azure PowerShell)', rem)
                for i in range(1, len(rem_split_results), 2):  # Start from index 1 and step by 2 to get delimiters
                    delimiter = rem_split_results[i].strip()  # Get the delimiter and remove leading/trailing whitespace
                    string = rem_split_results[i + 1].strip()  # Get the corresponding string and remove leading/trailing whitespace
                    rem_test.update({delimiter: string}) 
                rem_steps = rem_test
                rem_count += 1
            except IndexError:
                logger.info("*** Page does not contain Remediation ***")

            # Get Default Value by splits as WHEN PRESENT it is always between Default Value and CIS Controls,
            # Faster than regex
            # Found to be always present in Windows 2019 but NOT in RHEL 7
            try:
                defval_post = data.split("Default Value:", 1)[1]
                defval = defval_post.partition("CIS Controls:")[0].strip().replace('\n', '')
                defval_count += 1
            except IndexError:
                logger.info("*** Page does not contain Default Value ***")

            # Get CIS Controls by splits as they are always between CIS Controls and P a g e, regex the result
            try:
                cis_post = data.split("CIS Controls:", 1)[1]
                cis = cis_post.partition("P a g e")[0].strip().replace('\n', '')
                cis = re.sub("[^a-zA-Z0-9\\n.-]+", " ", cis)
                cis_count += 1
                # Incrementing defval_count if cis_count is found as Default Value is not always present (ex: RHEL7)
                if defval_count == (cis_count-1):
                    defval = ""
                    defval_count += 1
            except IndexError:
                logger.info("*** Page does not contain CIS Controls ***")

            # We only write to json if a parsed rule is fully assembled
            if rule_count:
                row_count = [
                    rule_count,
                    level_count,
                    description_count,
                    rat_count,
                    acnt,
                    rem_count,
                    #defval_count,
                    #cis_count,
                ]
                logging.debug(row_count)
                if row_count.count(row_count[0]) == len(row_count):
                    # Have we seen this rule before? If not, add it to rules_data
                    if row_count not in seenList:
                        seenList = [row_count]
                        logger.info("*** Adding the following rule to JSON data: ***")
                        rule_data = {
                            "Rule_number": rulenr,
                            "Rule": rule,
                            "Profile_applicability": level,
                            "Description": description,
                            "Rationale": rat,
                            "Impact": imp,
                            "Audit": audit_steps,
                            "Remediation": rem_steps,
                            "Default_value": defval,
                            "CIS_controls": cis
                        }
                        logger.info(rule_data)
                        rules_data.append(rule_data)
            page += 1
        else:
            logger.info("*** All pages parsed, exiting. ***")
            exit()

    # Write JSON data to file
    with open(args.out_file, 'w') as json_file:
        json.dump(rules_data, json_file, indent=4)


# Setup command line arguments
if __name__ == "__main__":
    main()
