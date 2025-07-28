#!/usr/bin/env python3
"""
Generate a cleanup report comparing original and cleaned data
"""

import pandas as pd


def generate_cleanup_report():
    """Generate a report showing the cleanup results"""
    
    print("Course Data Cleanup Report")
    print("=" * 50)
    
    # Load both files
    original_df = pd.read_csv("input/courses_export_2025-07-19.tsv", sep='\t')
    cleaned_df = pd.read_csv("output/courses_export_2025-07-19_cleaned.tsv", sep='\t')
    
    print(f"Original file: {len(original_df)} courses")
    print(f"Cleaned file: {len(cleaned_df)} courses")
    print()
    
    # Find courses with type field changes
    type_changes = 0
    dept_changes = 0
    
    print("Sample Type Field Cleanups:")
    print("-" * 30)
    
    sample_count = 0
    for idx, (orig_row, clean_row) in enumerate(zip(original_df.itertuples(), cleaned_df.itertuples())):
        if orig_row.type != clean_row.type:
            type_changes += 1
            if sample_count < 10:  # Show first 10 examples
                print(f"Course: {orig_row.code}")
                print(f"  Original: {orig_row.type}")
                print(f"  Cleaned:  {clean_row.type}")
                print()
                sample_count += 1
        
        # Check department/faculty changes
        if (orig_row.deliver_department != clean_row.deliver_department or 
            orig_row.deliver_faculty != clean_row.deliver_faculty):
            dept_changes += 1
    
    print(f"\nSummary:")
    print(f"- Courses with type field cleaned: {type_changes}")
    print(f"- Courses with department/faculty updated: {dept_changes}")
    
    # Check for remaining quote issues
    remaining_quotes = cleaned_df['type'].str.contains('["""]', na=False).sum()
    print(f"- Courses with remaining quotes in type field: {remaining_quotes}")
    
    if remaining_quotes > 0:
        print("\nCourses still with quotes:")
        quotes_df = cleaned_df[cleaned_df['type'].str.contains('["""]', na=False)]
        for _, row in quotes_df.head(5).iterrows():
            print(f"  {row['code']}: {row['type']}")


if __name__ == "__main__":
    generate_cleanup_report()
