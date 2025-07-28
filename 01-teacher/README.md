# Teacher Information Fetching

This module fetches teacher information from the BNBU official website.

## Overview

The `teacher-fetch.py` script scrapes teacher information from the [BNBU staff directory](https://staff.uic.edu.cn/) and exports the data in both JSON and CSV formats.

## Prerequisites

- Python 3.x
- Required packages for web scraping
- Internet connection

## Usage

To fetch teacher information:

```bash
python teacher-fetch.py
```

## Output Files

The script generates the following output files in the `output/` directory:

- `teachers.json` - Teacher information in JSON format
- `teachers.csv` - Teacher information in CSV format

## Data Structure

The exported teacher data typically includes:

- Teacher names
- Department/Faculty affiliation
- Contact information (if available)
- Academic titles/positions

## Notes

- The script automatically handles pagination and rate limiting
- Output files are saved in the `output/` directory
- Check the BNBU staff website for the most current data structure
