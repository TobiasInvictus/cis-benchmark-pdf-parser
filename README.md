# cis_pdf_parser.py

cis_pdf_parser.py is a python script for parsing CIS Benchmark PDF files from the [Center for Internet Security](https://www.cisecurity.org/cis-benchmarks/) into a CSV file format. As of August 2021, all benchmarks are only published in PDF format, which limits their usability. 

## Use Cases

This parser can be useful for the following use cases:

* This script's Comma Separated Value (CSV) output can be used to enhance security assessment result output from popular industry security assessment tools, which do not always include the Rationale, Audit, Remediation, and CIS Controls fields found in the full PDF version of the benchmark.
* This script can also be used to automate conversion of a CIS Benchmark PDF file upon each new version release, as other file formats are for CIS SecureSuite members only.
* This script's output is simple to further parse by its nature of being comma separated values, and can be ingested by other scripts or processes, such as a process which maps each CIS Control category to the user's chosen operating system benchmarks.

## Setup

cis_pdf_parser.py is dependent upon python3, the fitz, csv, re, logging, and argparse modules, and the script expects a path to a CIS Benchmark .pdf file and a filename to output to.

Run the following:
```
$ pip install -r requirements.txt
```

## Usage

```
$ python3 cis_pdf_parser.py --help
usage: cis_pdf_parser.py [-h] --pdf_file PDF_FILE --out_file OUT_FILE [-l LOG_LEVEL]

Parses CIS Benchmark PDF content into CSV Format

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --pdf_file PDF_FILE   PDF File to parse
  --out_file OUT_FILE   Output file in .csv format
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Set log level (DEBUG, INFO, etc). Default to INFO
```

## Examples

The script will parse each page and extractor information for the Azure CIS benchmarks and store them in the Azure.json file.
```
python json_cis_pdf_parser.py --pdf_file CIS_Microsoft_Azure_Foundations_Benchmark_v2.1.0.pdf --out_file Azure.json
```

The script will parse each page and extractor information for the Microsoft 365 CIS benchmarks and store them in the M365.json file.
```
python json_cis_pdf_parser.py --pdf_file CIS_Microsoft_365_Foundations_Benchmark_v3.1.0.pdf --out_file M365.json
```

Add the check numbers from the TODO.csv file to results.json. It needs Azure.json and M365.json to be in the root dir to extract the information from them.
```
python json_check_enricher.py
```

## Full Command Example:

```
$ python3 cis_pdf_parser.py --pdf_file CIS.pdf --out_file output.json
```

## Output

The script will parse each page and extract the information corresponding to the following fields:

```
Rule, Profile Applicability, Description, Rationale, Audit, Remediation, CIS Controls
```

## Testing Notes

**Tested against:**

* CIS Microsoft Azure Foundations Benchmark v2.1.0 - 02-13-2024


You will need provide a copy of or download the latest CIS Benchmark files from the [Center for Internet Security](https://learn.cisecurity.org/benchmarks).

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Contributors

* Tobias