# Course Description Extraction (CDE)

This module extracts course descriptions from official PDF documents released by BNBU Academic Registry.

## Overview

The `cd-extract.py` script processes PDF files containing course descriptions and extracts structured course information including course codes, names, prerequisites, units, and descriptions.

## Prerequisites

- Python 3.x
- Required packages (install with `pip install -r ../requirements-pdf.txt`)

## Usage

### Basic Extraction

To extract course descriptions from a PDF file:

```bash
python cd-extract.py <path_to_pdf>
```

### Export as TSV

To export results as TSV format:

```bash
python cd-extract.py <path_to_pdf> --export tsv
```

### Custom Output Prefix

To customize the output file name prefix:

```bash
python cd-extract.py <path_to_pdf> --export tsv --prefix <prefix>
```

## Input Requirements

- PDF files from [BNBU Academic Registry](https://ar.bnbu.edu.cn/info/1021/1430.htm)
- PDF files should be placed in the `input/` directory

## Output Files

For an input PDF file named `cd-20250702.pdf`, the script generates:

- `20250702-raw_lines.txt` - Raw lines extracted from the PDF
- `20250702.tsv` - Structured course data in TSV format

### TSV Output Format

The TSV file contains the following columns:

1. `course_code` - Course identifier (e.g., "ACCT3013")
2. `course_name` - Full course title
3. `prerequisite` - Course prerequisites
4. `unit` - Number of credit units
5. `course_description` - Detailed course description

## Example Files

Check the `input/` and `output/` directories for example files and expected output formats.
