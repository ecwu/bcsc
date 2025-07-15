import re
import string
import fitz
import csv
import argparse
import os
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Constants
SKIP_LINES = 6  # Number of lines to skip from beginning of PDF
PRINTABLE = set(string.printable)

# Remove control characters from printable set
PRINTABLE.remove('\t')
PRINTABLE.remove('\n')
PRINTABLE.remove('\x0b')
PRINTABLE.remove('\x0c')
PRINTABLE.remove('\r')

# Compiled regex patterns
COURSE_CODE_PATTERN = re.compile(r"([A-Z]{2,4}\d{4})")
COURSE_NAME_PATTERN = re.compile(r"^([A-Z]{2,4}\d{4}) ([0-9A-Z\s\-\(\)&\+\?,:]*)$")
UNIT_PATTERN = re.compile(r"\(\d{1}\s*(unit|UNIT).*\)")
PAGE_NUMBER_PATTERN = re.compile(r"\d+ / \d+")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def hanging_course_name(course_raw: List[str]) -> List[str]:
    """Extract hanging course name parts before parentheses."""
    buffer = []
    for line in course_raw:
        if "(" in line:
            break
        if line:
            buffer.append(line)
    return buffer

def get_course_code(course_name: str) -> Optional[str]:
    """Extract course code from course name."""
    result = COURSE_CODE_PATTERN.search(course_name)
    return result.group(1) if result else None

def get_course_name(course_name: str, course_raw: List[str]) -> str:
    """Extract and clean course name."""
    course_code = get_course_code(course_name)
    if not course_code:
        return course_name.strip()
    
    raw_course_name = course_name.replace(course_code, '')
    hanging = hanging_course_name(course_raw)
    full_course_name = ' '.join([raw_course_name.strip()] + hanging).strip()
    return full_course_name
    

def get_course_unit(course_raw: List[str]) -> Optional[str]:
    """Extract course unit from raw course data."""
    for line in course_raw:
        stripped_line = line.strip()
        if UNIT_PATTERN.match(stripped_line):
            # Extract the digit after the opening parenthesis
            return stripped_line[1:2]
    return None
        
def get_course_desc(course_raw: List[str]) -> List[str]:
    """Extract course description from raw course data."""
    buffer = []
    found_description = False
    description_markers = ["Course Description:", "Course  Description", "Description:", "Course Description"]
    
    for line in course_raw:
        if any(marker in line for marker in description_markers):
            found_description = True
        if found_description:
            buffer.append(line)
    return buffer
        
def get_course_pre(course_raw: List[str]) -> str:
    """Extract prerequisite information from raw course data."""
    buffer = []
    found_prereq = False
    description_markers = ["Course Description:", "Course  Description", "Description:", "Course Description"]
    
    for line in course_raw:
        if "Pre-requisite(s):" in line:
            found_prereq = True
        if any(marker in line for marker in description_markers):
            break
        if found_prereq:
            if "Pre-requisite(s):" in line:
                buffer.append(line.replace("Pre-requisite(s):", ""))
            else:
                buffer.append(line)
    return "".join(buffer)

def extract_filename_prefix(pdf_filename):
    """Extract filename prefix from PDF filename"""
    basename = os.path.basename(pdf_filename)
    name_without_ext = os.path.splitext(basename)[0]
    # Remove 'cd-' prefix if present
    if name_without_ext.startswith('cd-'):
        return name_without_ext[3:]
    return name_without_ext

def extract(pdf_filename, filename_prefix, save_tsv=False):
    """
    Extract course information from PDF file.
    
    Args:
        pdf_filename (str): Path to the PDF file
        filename_prefix (str): Prefix for output files
        save_tsv (bool): Whether to save TSV files (default: False)
    
    Returns:
        dict: Dictionary containing course information
    """
    logging.info(f"Loading PDF {pdf_filename}")

    with fitz.open(pdf_filename) as doc:  # open document
        text = chr(12).join([page.get_text() for page in doc])
        text = text.split('\n')
        text = ["".join(filter(lambda x: x in PRINTABLE, l)) for l in text][SKIP_LINES:]

    RAW_FILENAME = f"{filename_prefix}-raw_lines.txt"

    logging.info(f"There are {len(text)} lines of text in the PDF, saving to {RAW_FILENAME}")

    with open(RAW_FILENAME, 'w') as fp:
        for item in text:
            # write each item on a new line
            fp.write("%s\n" % item)
        logging.info("Done writing raw lines")

    cc_dict = defaultdict(int)
    for line in text:
        if COURSE_CODE_PATTERN.match(line):
            result = COURSE_CODE_PATTERN.search(line)
            if result:
                cc_dict[result.group(1)] += 1

    logging.info(f"Found {len(cc_dict.keys())} matched course code")

    # Use the pre-compiled pattern

    cn_list = list()  # Course Name List
    cd_list = list()  # Course Description List

    new_flag = 0
    temp_c_list = list()
    description_markers = ["Course Description:", "Course  Description", "Description:", "Course Description"]
    
    for k, line in enumerate(text):
        if COURSE_NAME_PATTERN.match(line):  # A new course pattern like string
            if new_flag == 1:  # *Course Description* flag not meet
                temp_c_list.append(line)  # Just another line
            else:  # *Course Description* flag meet
                if cn_list:
                    cd_list.append(temp_c_list)  # Save previous raw data
                    temp_c_list = []
                new_flag = 1
                cn_list.append(line)  # Save new course name
        elif any(marker in line for marker in description_markers):
            new_flag = 0
            temp_c_list.append(line)
        else:
            temp_c_list.append(line)
    cd_list.append(temp_c_list)

    logging.info(f"Found {len(cn_list)} Course Name, {len(cd_list)} Course Description (Two number equal means good)")

    course_dict = {}
    for n, r in zip(cn_list, cd_list):
        cc = get_course_code(n)
        if cc:  # Validate course code exists
            payload = {
                'course_code': cc,
                'course_name': get_course_name(n, r),
                'unit': get_course_unit(r),
                'prerequisite': get_course_pre(r),
                'description': get_course_desc(r)
            }
            course_dict[cc] = payload
        else:
            logging.warning(f"Could not extract course code from: {n}")

    if save_tsv:
        logging.info("Saving Course Records")

        try:
            with open(f'{filename_prefix}-records.tsv', 'w', newline='', encoding='utf-8') as tsv_file:
                writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
                writer.writerow(["course_code","course_name","prerequisite","unit"])
                for k, v in course_dict.items():
                    temp_prerequisite = v['prerequisite'].strip() if v['prerequisite'] else "N/A"
                    if "None" in temp_prerequisite or "None Course" in temp_prerequisite:
                        temp_prerequisite = "N/A"
                    writer.writerow([v['course_code'], v['course_name'], temp_prerequisite, v['unit']])
        except IOError as e:
            logging.error(f"Error writing records TSV file: {e}")
            raise

        code_desc_dict = dict()
        for k, v in course_dict.items():
            code_desc_dict[k] = v['description']

        for k, v in code_desc_dict.items():
            tv = [line for line in v if not PAGE_NUMBER_PATTERN.match(line.strip())]  # Clean up page number pattern 
            temp = ''.join(''.join(tv).split(":")[1:]).strip()
            code_desc_dict[k] = temp

        logging.info("Saving Course Descriptions")

        try:
            with open(f'{filename_prefix}-description.tsv', 'w', newline='', encoding='utf-8') as tsv_file:
                writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
                writer.writerow(["course_code","course_description"])
                for k, v in code_desc_dict.items():
                    writer.writerow([k, v])
        except IOError as e:
            logging.error(f"Error writing description TSV file: {e}")
            raise

        logging.info("Done, Exiting")
    
    return course_dict

def main():
    """Main function for direct script execution"""
    parser = argparse.ArgumentParser(description='Extract course information from PDF file')
    parser.add_argument('pdf_filename', help='Path to the PDF file to process')
    parser.add_argument('--tsv', action='store_true', help='Generate TSV files')
    parser.add_argument('--prefix', help='Custom filename prefix (default: extracted from PDF filename)')
    
    args = parser.parse_args()
    
    # Extract filename prefix from PDF filename if not provided
    if args.prefix:
        filename_prefix = args.prefix
    else:
        filename_prefix = extract_filename_prefix(args.pdf_filename)
    
    # Generate TSV files only if --tsv is specified
    save_tsv = args.tsv
    
    extract(args.pdf_filename, filename_prefix, save_tsv=save_tsv)

if __name__ == "__main__":
    main()