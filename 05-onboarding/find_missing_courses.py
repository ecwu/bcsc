#!/usr/bin/env python3
"""
Script to find courses that are missing in the input file but present in the output file.
Compares two TSV files based on course codes.

Usage:
    python find_missing_courses.py <input_file> <output_file>
    
Where:
    input_file: TSV file with course codes in 'code' column
    output_file: TSV file with course codes in 'course_code' column
"""

import argparse
import csv
import sys
from pathlib import Path


def load_course_codes(file_path, code_column):
    """
    Load course codes from a TSV file.
    
    Args:
        file_path (str): Path to the TSV file
        code_column (str): Name of the column containing course codes
        
    Returns:
        set: Set of course codes
    """
    course_codes = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            
            if code_column not in reader.fieldnames:
                print(f"Error: Column '{code_column}' not found in {file_path}")
                print(f"Available columns: {reader.fieldnames}")
                sys.exit(1)
            
            for row in reader:
                course_code = row[code_column].strip()
                if course_code:  # Only add non-empty codes
                    course_codes.add(course_code)
                    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except (UnicodeDecodeError, csv.Error) as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)
        
    return course_codes


def find_missing_courses(input_file, output_file):
    """
    Find courses that are in output_file but missing from input_file.
    
    Args:
        input_file (str): Path to input TSV file
        output_file (str): Path to output TSV file
        
    Returns:
        set: Set of missing course codes
    """
    print(f"Loading course codes from input file: {input_file}")
    input_codes = load_course_codes(input_file, 'code')
    print(f"Found {len(input_codes)} courses in input file")
    
    print(f"Loading course codes from output file: {output_file}")
    output_codes = load_course_codes(output_file, 'course_code')
    print(f"Found {len(output_codes)} courses in output file")
    
    # Find courses in output but not in input
    missing_courses = output_codes - input_codes
    
    return missing_courses, input_codes, output_codes


def get_course_details(file_path, course_codes, code_column):
    """
    Get detailed information for specific course codes from a TSV file.
    
    Args:
        file_path (str): Path to the TSV file
        course_codes (set): Set of course codes to look up
        code_column (str): Name of the column containing course codes
        
    Returns:
        list: List of dictionaries containing course details
    """
    course_details = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        
        for row in reader:
            if row[code_column].strip() in course_codes:
                course_details.append(row)
                
    return course_details


def main():
    parser = argparse.ArgumentParser(
        description='Find courses missing in input file but present in output file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python find_missing_courses.py input/courses_export_2025-07-19.tsv output/20250702.tsv
    python find_missing_courses.py /path/to/input.tsv /path/to/output.tsv
        """
    )
    
    parser.add_argument('input_file', help='Input TSV file (with "code" column)')
    parser.add_argument('output_file', help='Output TSV file (with "course_code" column)')
    parser.add_argument('--details', '-d', action='store_true', 
                       help='Show detailed information for missing courses')
    parser.add_argument('--stats', '-s', action='store_true',
                       help='Show additional statistics')
    
    args = parser.parse_args()
    
    # Validate input files exist
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist")
        sys.exit(1)
        
    if not Path(args.output_file).exists():
        print(f"Error: Output file '{args.output_file}' does not exist")
        sys.exit(1)
    
    print("=" * 60)
    print("COURSE COMPARISON ANALYSIS")
    print("=" * 60)
    
    # Find missing courses
    missing_courses, input_codes, output_codes = find_missing_courses(args.input_file, args.output_file)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if missing_courses:
        print(f"\nFound {len(missing_courses)} course(s) in output file but missing from input file:")
        print("-" * 40)
        
        missing_list = sorted(list(missing_courses))
        for i, course_code in enumerate(missing_list, 1):
            print(f"{i:2d}. {course_code}")
        
        if args.details:
            print("\n" + "=" * 60)
            print("DETAILED INFORMATION FOR MISSING COURSES")
            print("=" * 60)
            
            course_details = get_course_details(args.output_file, missing_courses, 'course_code')
            
            for detail in sorted(course_details, key=lambda x: x['course_code']):
                print(f"\nCourse Code: {detail['course_code']}")
                print(f"Course Name: {detail.get('course_name', 'N/A')}")
                print(f"Units: {detail.get('unit', 'N/A')}")
                print(f"Prerequisites: {detail.get('prerequisite', 'N/A')}")
                print(f"Description: {detail.get('course_description', 'N/A')[:100]}...")
                print("-" * 40)
    else:
        print("\n✓ No missing courses found! All courses in output file are present in input file.")
    
    if args.stats:
        # Additional statistics
        also_in_input = input_codes - output_codes
        
        print("\n" + "=" * 60)
        print("ADDITIONAL STATISTICS")
        print("=" * 60)
        print(f"Courses only in input file: {len(also_in_input)}")
        print(f"Courses only in output file: {len(missing_courses)}")
        print(f"Common courses: {len(input_codes & output_codes)}")
        
        if also_in_input and len(also_in_input) <= 20:  # Only show if reasonable number
            print("\nCourses in input but not in output:")
            for course in sorted(also_in_input):
                print(f"  - {course}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if not missing_courses else 1)


if __name__ == "__main__":
    main()
