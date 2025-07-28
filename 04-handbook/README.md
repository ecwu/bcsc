# Course Information Extraction from Handbooks

This module extracts course information from PDF handbook documents using the DeepSeek API.

## Overview

The `pdf_extract_courses.py` script processes PDF handbook files by extracting text from the second page and using AI to parse structured course data.

## Prerequisites

### 1. DeepSeek API Key
Set the `DEEPSEEK_API` environment variable:

```bash
export DEEPSEEK_API='your-api-key-here'
```

### 2. Required Python Packages
Install dependencies:

```bash
pip install PyPDF2 openai
```

## Usage

### Basic Usage (Default Directories)
Process all PDF files in the default handbooks directory:

```bash
python pdf_extract_courses.py
```

This uses:
- Input directory: `handbooks/2025`
- Output directory: `output/individual_courses/`

### Custom Input and Output Directories

```bash
python pdf_extract_courses.py --input-dir handbooks/2025 --output-dir output/individual_courses
```

### Create Combined Output File
Generate a single combined TSV file containing all courses:

```bash
python pdf_extract_courses.py --combined all_courses.tsv
```

### Full Example with All Options

```bash
python pdf_extract_courses.py \
    --input-dir handbooks/2025 \
    --output-dir output/individual_courses \
    --combined all_courses_2025.tsv
```

## Input Requirements

- PDF handbook files in the specified input directory
- PDF files should contain course information on the second page
- Files should be readable and contain extractable text

## Output Files

### Individual Course Files
For each processed PDF file, generates TSV files in the output directory:

- `DEPARTMENT_2025_pdf.tsv` (e.g., `ACCT_2025_pdf.tsv`, `CST_2025_pdf.tsv`)

### Combined Output File (Optional)
If `--combined` flag is used, creates a single TSV file containing all extracted courses.

### TSV Output Format
TSV columns:

1. `course_code` - Course identifier (e.g., "ACCT3013", "CST2023")
2. `course_name` - Full course title
3. `unit` - Number of credit units
4. `source_file` - Original PDF filename for reference

## API Usage

The script uses the DeepSeek API to intelligently parse course information from PDF text. The AI model:

- Identifies course codes, names, and units
- Handles various PDF formatting styles
- Provides structured JSON output
- Maintains accuracy across different handbook formats

## Example Files

Check the `handbooks/` and `output/` directories for example PDF files and expected output formats.
