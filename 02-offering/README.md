# Course Offerings Extraction

This module extracts course offering information from Excel timetable files, including course codes, lecturers, years, and semesters.

## Overview

The scripts in this directory process Excel timetable files to generate:
- Course-lecturer relationships
- Department/faculty information
- Unified department mappings

## Scripts

### `offering-extract.py`
Main extraction script for processing Excel timetable files.

### `merge-departments.py`
Merges department information across multiple semesters into a unified mapping.

## Prerequisites

- Python 3.x
- Required packages for Excel processing (pandas, openpyxl)
- Excel timetable files in the `input/` directory

## Usage

### Test Mode (Default)
Test parsing all Excel files without generating output:

```bash
python offering-extract.py
```

### Generate Course Offerings
Process all Excel files and generate CSV files:

```bash
python offering-extract.py --process
```

### Generate Department Information
Extract department/faculty information:

```bash
python offering-extract.py --departments
```

### Merge Department Data
Create unified department mapping:

```bash
python merge-departments.py
```

## Input Requirements

Excel files should be placed in the `input/` folder with columns:
- `Course Code` (required)
- `Teachers` (required for offering extraction)
- `Offering Unit` (for department extraction)
- `Offering Programme` (for department extraction)

## Output Files

### Course Offerings (`--process`)
- `offering-YYYY-SEMESTER.csv` files with columns:
  1. `course_code` - Course identifier
  2. `year` - Academic year
  3. `semester` - FALL or SPRING
  4. `lecturer_name` - Instructor name

### Department Information (`--departments`)
- `departments-YYYY-SEMESTER.tsv` files with columns:
  1. `Course Code` - Course identifier
  2. `Year` - Academic year
  3. `Semester` - FALL or SPRING
  4. `Offering Unit` - Department/Faculty unit
  5. `Offering Programme` - Programme information

### Unified Department Mapping
- `departments-unified.tsv` - Consolidated department mappings across all semesters

## Example Files

Check the `input/` and `output/` directories for example Excel files and expected output formats.
