# Course Data Onboarding and Cleanup

This module contains scripts for processing and cleaning course data for database onboarding, including missing course detection, data cleanup, and format standardization.

## Overview

The scripts handle the complete pipeline for preparing course data:

- Finding missing courses between datasets
- AI-enhanced course name processing and translation
- Data cleanup and standardization
- Format conversion for database import

## Scripts

### `course_onboarding.py`
Main onboarding script that finds missing courses and converts them to proper TSV format with AI processing.

### `course-cleanup.py`
Cleans up course data from production by processing type fields and updating department information.

### `find_missing_courses.py`
Compares two TSV files to identify courses that exist in one file but not the other.

### `cleanup-report.py`
Generates cleanup reports and statistics.

### Test Scripts
- `test_limited.py` - Limited testing functionality
- `test_processing.py` - Processing pipeline tests

## Prerequisites

### For Course Onboarding
- Ollama service running locally (default: `http://localhost:11434`)
- Required model (default: `qwen3:30b-a3b`)
- Python 3.x with required packages

### For Course Cleanup
- `departments-unified.tsv` file for department mapping
- Production course data export file

## Usage

### 1. Course Onboarding

Find missing courses and convert to TSV format:

```bash
python course_onboarding.py input/courses_export.tsv output/reference_courses.tsv
```

With custom options:

```bash
python course_onboarding.py input/courses_export.tsv output/reference_courses.tsv \
    --ollama-host http://localhost:11434 \
    --output-tsv onboarding_courses.tsv \
    --model qwen3:30b-a3b \
    --verbose
```

### 2. Course Data Cleanup

Clean production course data:

```bash
python course-cleanup.py
```

### 3. Find Missing Courses

Compare two TSV files:

```bash
python find_missing_courses.py input/courses_export.tsv output/reference_courses.tsv
```

## Input Requirements

### Course Onboarding
- Input TSV file with `code` column containing course codes
- Output TSV file with `course_code` column for comparison
- Ollama service running with specified model

### Course Cleanup
- Production course data export file (TSV format)
- `departments-unified.tsv` file for department mapping

## Output Files

### Course Onboarding Output
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

### Course Cleanup Output
`courses_export_YYYY-MM-DD_cleaned.tsv` - Cleaned version with:

- Cleaned type fields (no duplicate quotes)
- Updated department and faculty information
- Standardized formatting

## AI Features

The onboarding script uses AI for:

- Converting course names to proper capitalization
- Translating English names and descriptions to Chinese
- Maintaining consistency across course data
- Enhancing data quality automatically

## Example Files

Check the `input/` and `output/` directories for example files and expected formats.
