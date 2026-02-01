#!/usr/bin/env python3
"""
Combine multiple semester CSV files into a single CSV file.

This script finds all CSV files matching a given prefix, combines them
into one file, and displays statistics about the combined data.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def load_csv_data(filepath: Path) -> List[Dict[str, str]]:
    """
    Load CSV data from file.

    Args:
        filepath: Path to CSV file

    Returns:
        List of dictionaries representing CSV rows
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV '{filepath}': {e}")
        sys.exit(1)


def find_matching_files(prefix: str) -> List[Path]:
    """
    Find all CSV files matching the given prefix.

    Args:
        prefix: File path prefix (e.g., "input/offering-v2-")

    Returns:
        Sorted list of matching file paths
    """
    prefix_path = Path(prefix)
    directory = prefix_path.parent if prefix_path.parent else Path('.')
    file_pattern = prefix_path.name + '*.csv'

    matching_files = sorted(directory.glob(file_pattern))

    if not matching_files:
        print(f"Error: No files found matching '{prefix}*.csv'")
        print(f"  Searched in directory: {directory.absolute()}")
        print(f"  Pattern: {file_pattern}")
        sys.exit(1)

    return matching_files


def combine_csv_files(files: List[Path]) -> Tuple[List[Dict[str, str]], Dict[str, int]]:
    """
    Combine data from multiple CSV files.

    Args:
        files: List of CSV file paths

    Returns:
        Tuple of (combined_data, file_stats)
    """
    combined_data = []
    file_stats = {}

    for filepath in files:
        data = load_csv_data(filepath)
        combined_data.extend(data)
        file_stats[str(filepath.name)] = len(data)

    return combined_data, file_stats


def display_stats(combined_data: List[Dict[str, str]], file_stats: Dict[str, int]) -> None:
    """
    Display statistics about the combined data.

    Args:
        combined_data: Combined data from all files
        file_stats: Dictionary of record counts per file
    """
    total_records = len(combined_data)

    print("\n=== File Statistics ===")
    for filename, count in sorted(file_stats.items()):
        print(f"  {filename}: {count:,} records")

    print(f"\n=== Combined Statistics ===")
    print(f"  Total files: {len(file_stats)}")
    print(f"  Total records: {total_records:,}")

    unique_courses = set(row.get('course_code', '') for row in combined_data if row.get('course_code'))
    print(f"  Unique courses: {len(unique_courses):,}")

    unique_lecturers = set(row.get('lecturer_name', '') for row in combined_data if row.get('lecturer_name'))
    print(f"  Unique lecturers: {len(unique_lecturers):,}")

    unique_sessions = set(row.get('session', '') for row in combined_data if row.get('session'))
    print(f"  Unique sessions: {len(unique_sessions):,}")

    year_semester_counts: Dict[str, int] = {}
    for row in combined_data:
        year = row.get('year', '')
        semester = row.get('semester', '')
        if year and semester:
            key = f"{year}-{semester}"
            year_semester_counts[key] = year_semester_counts.get(key, 0) + 1

    if year_semester_counts:
        print(f"\n  By Year-Semester:")
        for key, count in sorted(year_semester_counts.items()):
            print(f"    {key}: {count:,} records")


def check_missing_sessions(data: List[Dict[str, str]]) -> None:
    """
    Check for records with missing session field.

    Args:
        data: Combined data from all files
    """
    missing_session_rows = []

    for idx, row in enumerate(data):
        session = row.get('session', '')
        if not session or session.strip() == '':
            missing_session_rows.append({
                'index': idx,
                'course_code': row.get('course_code', ''),
                'year': row.get('year', ''),
                'semester': row.get('semester', ''),
                'lecturer_name': row.get('lecturer_name', ''),
                'schedule': row.get('schedule', '')
            })

    if missing_session_rows:
        print(f"\n=== MISSING SESSION FIELDS WARNING ===")
        print(f"  Total records missing session: {len(missing_session_rows):,}")
        print(f"\n  First 20 examples:")
        for i, row in enumerate(missing_session_rows[:20], 1):
            print(f"    {i}. {row['course_code']} | {row['year']}-{row['semester']} | {row['lecturer_name']} | Schedule: {row['schedule'][:50]}...")

        if len(missing_session_rows) > 20:
            print(f"    ... and {len(missing_session_rows) - 20} more")
    else:
        print(f"\n=== Session Field Check ===")
        print(f"  All records have session field ✓")


def write_combined_data(
    data: List[Dict[str, str]],
    output_path: Path
) -> None:
    """
    Write combined data to CSV file.

    Args:
        data: List of dictionaries representing rows
        output_path: Path to output CSV file
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not data:
            print("Warning: No data to write")
            return

        fieldnames = list(data[0].keys())

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"\nOutput file: {output_path}")
        print(f"Total records written: {len(data):,}")
    except Exception as e:
        print(f"Error writing CSV: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Combine multiple semester CSV files into one file'
    )
    parser.add_argument(
        'prefix',
        help='File prefix pattern (e.g., "input/offering-v2-" or "output/offering-v2-")'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: combined-{prefix}.csv in output directory)'
    )

    args = parser.parse_args()

    # Find matching files
    print(f"Searching for files matching: {args.prefix}*.csv")
    matching_files = find_matching_files(args.prefix)

    print(f"Found {len(matching_files)} files:")
    for filepath in matching_files:
        print(f"  - {filepath.name}")

    combined_data, file_stats = combine_csv_files(matching_files)

    display_stats(combined_data, file_stats)

    check_missing_sessions(combined_data)

    if args.output:
        output_path = Path(args.output)
    else:
        prefix_name = Path(args.prefix).name
        output_filename = f"combined-{prefix_name}.csv"
        output_path = Path(__file__).parent / 'output' / output_filename

    write_combined_data(combined_data, output_path)


if __name__ == '__main__':
    main()
