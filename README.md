# BCSC - BNBU Course Script Collection

## Course Description Extraction

Location: `00-cde/cd-extract.py`

The script is designed to extract course descriptions from the Official released PDF documents. You need to provide the path to the PDF file containing the course descriptions. You can retrieve course descriptions from the [BNBU Academic Registry](https://ar.uic.edu.cn/info/1021/1430.htm).

### Usage

To run the script, use the following command in your terminal:

```bash
python cd-extract.py <path_to_pdf>
```

You want to export TSV files, so you can use the following command:

```bash
python cd-extract.py <path_to_pdf> --export tsv
```

You want to customize the output file name prefix, you can use the following command:

```bash
python cd-extract.py <path_to_pdf> --export tsv --prefix <prefix>
```

### Output Files

If the input PDF file is named `cd-20250702.pdf`, the script will generate the following output files:

- `20250702-raw_lines.txt` Contains the raw lines extracted from the PDF.
- `20250702.tsv` Contains the extracted course descriptions in TSV format.

The TSV file will have the following columns:
1. `course_code`
2. `course_name`
3. `prerequisite`
4. `unit`
5. `course_description`

## Teacher Information Fetching

Location: `01-teacher/teacher-fetch.py`

The script is designed to fetch teacher information from the [BNBU official website](https://staff.uic.edu.cn/).

### Usage
To run the script, use the following command in your terminal:

```bash
python teacher-fetch.py
```

### Output Files

The script will generate the following output files:

- `teachers.json` Contains the fetched teacher information in JSON format.
- `teachers.csv` Contains the fetched teacher information in CSV format.

## Course Offerings Extraction

Location: `02-offering/offering-extract.py`

The script is designed to extract course offering information (course codes, lecturers, years, and semesters) from Excel timetable files. It can process multiple Excel files and generate CSV files with course-lecturer relationships for each semester.

### How to Use

#### Test Excel Files (Default)

To test parsing all Excel files without generating output:

```bash
python offering-extract.py
```

#### Generate Course Offerings CSV Files

To process all Excel files and generate CSV files with course offerings:

```bash
python offering-extract.py --process
```

#### Generate Department Information TSV Files

To process all Excel files and extract department/faculty information:

```bash
python offering-extract.py --departments
```

### Input Requirements

The script expects Excel files to be placed in the `input/` folder relative to the script location. The Excel files should contain course timetable data with the following columns:

- `Course Code` (required)
- `Teachers` (required for offering extraction)
- `Offering Unit` (for department extraction)
- `Offering Programme` (for department extraction)

### Generated Output Files

#### Course Offerings (--process flag)

For each processed Excel file, generates CSV files in the `output/` folder:

- `offering-YYYY-SEMESTER.csv` (e.g., `offering-2024-FALL.csv`, `offering-2025-SPRING.csv`)

CSV columns:

1. `course_code` - Course identifier
2. `year` - Academic year
3. `semester` - FALL or SPRING
4. `lecturer_name` - Instructor name (cleaned and split if multiple)

#### Department Information (--departments flag)

For each processed Excel file, generates TSV files in the `output/` folder:

- `departments-YYYY-SEMESTER.tsv` (e.g., `departments-2024-FALL.tsv`)

TSV columns:

1. `Course Code` - Course identifier
2. `Year` - Academic year
3. `Semester` - FALL or SPRING
4. `Offering Unit` - Department/Faculty unit
5. `Offering Programme` - Programme information (if available)

## Course Information Extraction from Handbooks

Location: `04-handbook/pdf_extract_courses.py`

The script is designed to extract course information from PDF handbook documents using the DeepSeek API. It processes PDF files by extracting text from the second page and using AI to parse structured course data.

### Prerequisites

Before using this script, you need:

1. **DeepSeek API Key**: Set the `DEEPSEEK_API` environment variable
2. **Required Python packages**: Install dependencies with `pip install PyPDF2 openai`

```bash
export DEEPSEEK_API='your-api-key-here'
pip install PyPDF2 openai
```

### How to Use the Handbook Extraction

#### Basic Usage (Default Directories)

To process all PDF files in the default handbooks directory:

```bash
python pdf_extract_courses.py
```

This uses the default input directory `assets/handbooks/2025` and outputs to `output/individual_courses/`.

#### Custom Input and Output Directories

```bash
python pdf_extract_courses.py --input-dir handbooks/2025 --output-dir output/individual_courses
```

#### Create Combined Output File

To also generate a single combined TSV file containing all courses:

```bash
python pdf_extract_courses.py --combined all_courses.tsv
```

### Handbook Input Requirements

The script expects:

- PDF handbook files in the specified input directory
- PDF files should contain course information on the second page
- Files should be readable and contain extractable text

### Handbook Output Files

#### Individual Course Files

For each processed PDF file, generates TSV files in the output directory:

- `DEPARTMENT_2025_pdf.tsv` (e.g., `ACCT_2025_pdf.tsv`, `CST_2025_pdf.tsv`)

TSV columns:

1. `course_code` - Course identifier (e.g., "ACCT3013", "CST2023")
2. `course_name` - Full course title
3. `unit` - Number of credit units
4. `source_file` - Original PDF filename for reference

#### Combined Output File (Optional)

If `--combined` flag is used, creates a single TSV file containing all extracted courses from all processed PDFs.

## Course Data Onboarding and Cleanup

Location: `05-onboarding/`

This directory contains scripts for processing and cleaning course data for database onboarding. The scripts handle missing course detection, data cleanup, and format standardization.

### Main Scripts

#### 1. Course Onboarding (`course_onboarding.py`)

Finds courses missing in the input file but present in the output file, then converts them into proper TSV format with AI-enhanced processing.

**Prerequisites:**

- Ollama service running locally (default: `http://localhost:11434`)
- Required model (default: `qwen3:30b-a3b`)

**Usage:**

```bash
python course_onboarding.py input/courses_export.tsv output/reference_courses.tsv
```

**With custom options:**

```bash
python course_onboarding.py input/courses_export.tsv output/reference_courses.tsv \
    --ollama-host http://localhost:11434 \
    --output-tsv onboarding_courses.tsv \
    --model qwen3:30b-a3b \
    --verbose
```

**Features:**

- Finds missing courses between input and output files
- Converts course names to proper capitalization using AI
- Translates English names and descriptions to Chinese
- Generates properly formatted TSV with all required fields

#### 2. Course Data Cleanup (`course-cleanup.py`)

Cleans up course data from the production environment by processing type fields and updating department information.

**Usage:**

```bash
python course-cleanup.py
```

**Features:**

- Cleans the type field by removing unwanted quotes and duplicates
- Updates `deliver_department` and `deliver_faculty` based on `departments-unified.tsv`
- Processes the input file and generates a cleaned version

#### 3. Find Missing Courses (`find_missing_courses.py`)

Compares two TSV files to identify courses that exist in one file but not the other.

**Usage:**

```bash
python find_missing_courses.py input/courses_export.tsv output/reference_courses.tsv
```

**Features:**

- Compares course codes between two TSV files
- Input file should have `code` column
- Output file should have `course_code` column
- Reports missing courses with detailed statistics

### Onboarding Input Requirements

#### For Course Onboarding

- Input TSV file with `code` column containing course codes
- Output TSV file with `course_code` column for comparison
- Ollama service running with specified model

#### For Course Cleanup

- Production course data export file (TSV format)
- `departments-unified.tsv` file for department mapping

### Onboarding Output Files

#### Course Onboarding Output

`onboarding_courses.tsv` with columns:

1. `code` - Course identifier
2. `name_en` - English course name (AI-processed)
3. `name_cn` - Chinese course name (AI-translated)
4. `type` - Course type information
5. `units` - Number of credit units
6. `deliver_department` - Delivering department
7. `deliver_faculty` - Delivering faculty
8. `prerequisites` - Course prerequisites
9. `exclusions` - Course exclusions
10. `description` - Course description
11. `is_visible` - Visibility flag

#### Course Cleanup Output

`courses_export_YYYY-MM-DD_cleaned.tsv` - Cleaned version of the input file with:

- Cleaned type fields (no duplicate quotes)
- Updated department and faculty information
- Standardized formatting
