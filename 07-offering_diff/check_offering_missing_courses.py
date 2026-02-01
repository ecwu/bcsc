#!/usr/bin/env python3
import csv
import glob
from pathlib import Path
from collections import defaultdict


def load_course_codes_from_tsv(tsv_path: str) -> set:
    course_codes = set()
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            code = row.get('code', '').strip()
            if code:
                course_codes.add(code)
    return course_codes


def parse_offering_filename(filename: str) -> str:
    return filename.replace('offering-', '').replace('.csv', '')


def collect_missing_course_offerings(offering_path: str, existing_codes: set, 
                                     missing_courses: dict, seen_codes: set):
    filename = Path(offering_path).name
    semester = parse_offering_filename(filename)
    
    with open(offering_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            course_code = row.get('course_code', '').strip()
            if course_code and course_code not in existing_codes:
                if course_code not in missing_courses:
                    missing_courses[course_code] = {'semesters': []}
                if course_code not in seen_codes:
                    seen_codes.add(course_code)
                if semester not in missing_courses[course_code]['semesters']:
                    missing_courses[course_code]['semesters'].append(semester)


def main():
    script_dir = Path(__file__).parent
    tsv_files = list(script_dir.glob('courses_export_*.tsv'))
    
    if not tsv_files:
        print("Error: No courses_export_*.tsv file found")
        exit(1)
    
    courses_tsv = tsv_files[0]
    print(f"Loading courses from: {courses_tsv.name}")
    
    existing_codes = load_course_codes_from_tsv(str(courses_tsv))
    print(f"Found {len(existing_codes)} courses in TSV\n")
    
    offering_files = sorted(script_dir.glob('offering-*.csv'))
    
    if not offering_files:
        print("No offering-*.csv files found")
        exit(1)
    
    missing_courses = {}
    seen_codes = set()
    
    for offering_file in offering_files:
        collect_missing_course_offerings(
            str(offering_file), existing_codes, missing_courses, seen_codes
        )
    
    if missing_courses:
        print("=== Missing Courses (not in courses TSV) ===")
        print(f"{'Course Code':<15} {'Offered In'}")
        print("-" * 70)
        
        def extract_year_sem(semester_str):
            parts = semester_str.split('-')
            year = int(parts[0])
            sem_order = 1 if parts[1] == 'SPRING' else 2
            return (year, sem_order)
        
        def sort_key(item):
            course_code, info = item
            semesters = info['semesters']
            semester_keys = [extract_year_sem(s) for s in semesters]
            last_offer = max(semester_keys) if semester_keys else (0, 0)
            offer_count = len(semesters)
            return (-last_offer[0], -last_offer[1], -offer_count, course_code)
        
        sorted_courses = sorted(missing_courses.items(), key=sort_key)
        
        for course_code, info in sorted_courses:
            semesters = ", ".join(sorted(info['semesters']))
            print(f"{course_code:<15} {semesters}")
        
        print(f"\nTotal unique missing courses: {len(missing_courses)}")
    else:
        print("All courses in offerings are present in the TSV file!")


if __name__ == '__main__':
    main()
