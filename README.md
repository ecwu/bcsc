# BCSC - BNBU Course Script Collection

A comprehensive collection of Python scripts for extracting, processing, and managing course data from various sources at Beijing Normal University - Hong Kong (BNBU).

## Overview

This toolkit provides automated solutions for:

- **Course Description Extraction** - Extract structured course data from PDF documents
- **Teacher Information Fetching** - Scrape teacher information from university websites
- **Course Offerings Processing** - Parse Excel timetables to generate course-lecturer relationships
- **Handbook Data Extraction** - AI-powered extraction from PDF handbooks using DeepSeek API
- **Data Onboarding & Cleanup** - Process and standardize course data for database import

## Data Disclaimer

⚠️ **Important Notice**: This repository contains only the processing scripts and tools. **We do not provide any actual course data, PDF files, or university materials** due to copyright restrictions and privacy concerns.

**You must obtain the required data yourself from official sources:**

- Course description PDFs from [BNBU Academic Registry](https://ar.uic.edu.cn/info/1021/1430.htm)
- Excel timetable files from official university sources
- PDF handbook files from university filebase/academic systems
- Any other required input files from authorized university channels

**Users are responsible for ensuring they have proper authorization to access and process university data.**

## Quick Start

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements-pdf.txt`
3. **Set up API keys** (for handbook extraction): `export DEEPSEEK_API='your-key'`
4. **Obtain required data files** from official university sources (see disclaimer above)
5. **Navigate to the specific module** and follow the detailed instructions in each README

## Modules

### 📄 [00-cde](./00-cde/README.md) - Course Description Extraction
Extract course descriptions from official PDF documents.

```bash
cd 00-cde
python cd-extract.py <path_to_pdf> --export tsv
```

### 👥 [01-teacher](./01-teacher/README.md) - Teacher Information Fetching
Fetch teacher information from the BNBU staff website.

```bash
cd 01-teacher
python teacher-fetch.py
```

### 📊 [02-offering](./02-offering/README.md) - Course Offerings Extraction
Process Excel timetables to extract course offerings and department information.

```bash
cd 02-offering
python offering-extract.py --process
python offering-extract.py --departments
```

### 📚 [04-handbook](./04-handbook/README.md) - Handbook Data Extraction
AI-powered extraction from PDF handbooks using DeepSeek API.

```bash
cd 04-handbook
export DEEPSEEK_API='your-api-key'
python pdf_extract_courses.py --input-dir handbooks/2025
```

### 🔧 [05-onboarding](./05-onboarding/README.md) - Data Onboarding & Cleanup
Process and clean course data for database import with AI enhancement.

```bash
cd 05-onboarding
python course_onboarding.py input/courses_export.tsv output/reference_courses.tsv
python course-cleanup.py
```

## Project Structure

```
autoauto/
├── 00-cde/          # Course Description Extraction
├── 01-teacher/      # Teacher Information Fetching
├── 02-offering/     # Course Offerings Processing
├── 04-handbook/     # Handbook Data Extraction
├── 05-onboarding/   # Data Onboarding & Cleanup
└── README.md        # This file
```

## Prerequisites

- Python 3.x
- Required packages (see `requirements-pdf.txt`)
- DeepSeek API key (for handbook extraction)
- Ollama service (for onboarding AI features)

## Data Flow

1. **Extract** course descriptions from PDFs (`00-cde`)
2. **Fetch** teacher information (`01-teacher`)
3. **Process** timetable data (`02-offering`)
4. **Extract** handbook courses with AI (`04-handbook`)
5. **Onboard** and clean data for database (`05-onboarding`)

## Getting Help

For detailed usage instructions, examples, and troubleshooting:

- Check the individual README files in each module directory
- Review example input/output files in each module's directories
- Ensure all prerequisites are met before running scripts

## Contributing

When adding new features or scripts:

1. Follow the existing directory structure
2. Update the relevant module README
3. Add example files where appropriate
4. Update this main README if adding new modules
