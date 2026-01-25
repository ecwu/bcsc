# AGENTS.md - Agent Guidelines for autoauto Repository

## Overview
This is a Python-based course data extraction toolkit for Beijing Normal Hong Kong Baptist University (BNBU). The repository processes course descriptions, teacher information, course offerings, and handbook data using various external APIs and services.

## Build & Installation Commands

### Install Dependencies
```bash
pip install -r requirements-pdf.txt
```

### Running Scripts
Scripts are executed directly with Python:
```bash
python <module>/<script-name>.py [options]
```

### Testing
No formal test framework. Test scripts are run directly:
```bash
python 05-onboarding/test_processing.py
python 05-onboarding/test_limited.py
```

## Code Style Guidelines

### Formatting
- Use 4 spaces for indentation
- Maximum line length: not strictly enforced, but keep lines readable (~100-120 chars)
- Use blank lines between logical sections in functions
- Trailing whitespace should be avoided

### Imports
1. **Order**: Standard library → third-party packages → local imports
2. **Group imports** by category with blank lines between groups:
   ```python
   import re
   import csv
   import sys
   
   import requests
   import pandas as pd
   
   from typing import Dict, List, Optional
   ```
3. **Avoid wildcard imports** (`from module import *`)

### Type Hints
- Use type hints for function parameters and return values where appropriate
- Import from `typing` module:
  ```python
  from typing import Dict, List, Optional, Tuple, Set
  ```
- Not required for all functions, but encouraged for complex signatures

### Naming Conventions
- **Functions**: `snake_case` (e.g., `extract_course_info`, `load_teachers`)
- **Variables**: `snake_case` (e.g., `course_code`, `teacher_list`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SKIP_LINES`, `DEFAULT_TIMEOUT`)
- **Classes**: `PascalCase` (e.g., `CourseOnboardingTool`, `OllamaClient`)
- **Files/Saved outputs**: lowercase with hyphens (e.g., `offering-2025-FALL.csv`)

### Error Handling
- Use `try-except` blocks for operations that may fail
- Log/print meaningful error messages
- Use `sys.exit(1)` for critical failures (e.g., missing required files)
- Include specific exception types where appropriate:
  ```python
  try:
      with open(filename, 'r', encoding='utf-8') as f:
          data = json.load(f)
  except FileNotFoundError:
      print(f"Error: File '{filename}' not found")
      sys.exit(1)
  except json.JSONDecodeError as e:
      print(f"Error parsing JSON: {e}")
      sys.exit(1)
  ```

### File I/O
- **Encoding**: Always specify `encoding='utf-8'` when opening text files
- **TSV/CSV**: Use `csv` module with appropriate delimiter:
  ```python
  reader = csv.DictReader(file, delimiter='\t')
  writer = csv.DictWriter(file, fieldnames=fields, delimiter='\t')
  ```
- **Paths**: Use `pathlib.Path` for path operations (modern, cross-platform):
  ```python
  from pathlib import Path
  script_dir = Path(__file__).parent
  output_path = script_dir / 'output' / 'data.tsv'
  output_path.parent.mkdir(parents=True, exist_ok=True)
  ```

### Logging
- Use Python's `logging` module for scripts that generate significant output
- Configure basic logging at module level:
  ```python
  import logging
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
  ```
- Use `print()` for user-facing output and simple scripts
- Use `logging` for debugging, progress tracking, and warnings

### Docstrings & Comments
- **Module docstrings**: Triple-quoted string at top of file explaining purpose
- **Function docstrings**: Describe purpose, parameters, return values:
  ```python
  def extract_course_data(pdf_path: str) -> Dict:
      """
      Extract course data from PDF file.

      Args:
          pdf_path (str): Path to PDF file

      Returns:
          Dict: Dictionary containing course information
      """
  ```
- **Comments**: Use inline comments for complex logic, but prefer clear code over comments

### Shebang
Include shebang for executable scripts:
```python
#!/usr/bin/env python3
```

### Module Structure
- Each module (00-cde, 01-teacher, etc.) is self-contained
- Keep module dependencies minimal
- Use `input/` and `output/` directories within each module
- Include README.md in each module directory

### API Integration
- **DeepSeek API**: Set `DEEPSEEK_API` environment variable
- **Ollama**: Default host `http://localhost:11434`, configurable via CLI args
- **Web scraping**: Use `requests` with proper timeout and error handling:
  ```python
  try:
      response = requests.get(url, timeout=10)
      response.raise_for_status()
  except requests.RequestException as e:
      print(f"Request failed: {e}")
  ```

### Command Line Arguments
Use `argparse` for CLI scripts:
```python
import argparse

parser = argparse.ArgumentParser(description='Script description')
parser.add_argument('input_file', help='Input file path')
parser.add_argument('--option', help='Optional flag')
args = parser.parse_args()
```

## Project-Specific Notes

### Data Flow
1. `00-cde`: Extract course descriptions from PDFs → TSV
2. `01-teacher`: Fetch teacher data from web → JSON/CSV
3. `02-offering`: Process Excel timetables → CSV (offerings), TSV (departments)
4. `04-handbook`: Extract handbook data using DeepSeek API → TSV
5. `05-onboarding`: Process and clean course data → TSV for database import

### Dependencies
- **PDF processing**: `PyMuPDF` (fitz), `PyPDF2`
- **Excel processing**: `pandas`, `openpyxl`, `xlrd`
- **API clients**: `openai` (for DeepSeek), `requests` (for web/Ollama)
- **Data handling**: `csv`, `json`, built-in data structures

### External Services
- **DeepSeek API**: Used for AI-powered text extraction and translation
- **Ollama**: Local LLM service for course name processing and requirements
