#!/usr/bin/env python3
"""
Course Data Cleanup Script

This script cleans up the course data from the production environment by:
1. Cleaning the type field - removing unwanted quotes and duplicates
2. Updating deliver_department and deliver_faculty based on departments-unified.tsv
"""

import pandas as pd
import re
from collections import OrderedDict


def clean_type_field(type_str):
    """
    Clean the type field by removing unwanted quotes and duplicates.
    
    Args:
        type_str: The original type string
        
    Returns:
        str: Cleaned type string with no quotes and no duplicates
    """
    if pd.isna(type_str) or type_str == '':
        return ''
    
    # Remove all quotes (both " and """)
    cleaned = re.sub(r'["""]', '', str(type_str))
    
    # Split by comma and strip whitespace
    types = [t.strip() for t in cleaned.split(',') if t.strip()]
    
    # Remove duplicates while preserving order
    unique_types = list(OrderedDict.fromkeys(types))
    
    return ','.join(unique_types)


def load_departments_mapping(departments_file):
    """
    Load the departments mapping from departments-unified.tsv
    
    Args:
        departments_file: Path to departments-unified.tsv
        
    Returns:
        dict: Mapping of course code to (deliver_faculty, deliver_department)
    """
    try:
        df = pd.read_csv(departments_file, sep='\t')
        mapping = {}
        
        for _, row in df.iterrows():
            course_code = row['Course Code']
            offering_unit = row['Offering Unit']  # This maps to deliver_faculty
            offering_programme = row['Offering Programme']  # This maps to deliver_department
            
            # Use the most recent entry for each course (assuming data is sorted)
            mapping[course_code] = (offering_unit, offering_programme)
            
        print(f"Loaded {len(mapping)} course mappings from departments file")
        return mapping
        
    except Exception as e:
        print(f"Error loading departments mapping: {e}")
        return {}


def cleanup_course_data(input_file, output_file, departments_file):
    """
    Clean up the course data file.
    
    Args:
        input_file: Path to input TSV file
        output_file: Path to output TSV file  
        departments_file: Path to departments-unified.tsv
    """
    try:
        # Load the course data
        print(f"Loading course data from {input_file}")
        df = pd.read_csv(input_file, sep='\t')
        print(f"Loaded {len(df)} courses")
        
        # Load departments mapping
        departments_mapping = load_departments_mapping(departments_file)
        
        # Clean the type field
        print("Cleaning type field...")
        df['type'] = df['type'].apply(clean_type_field)
        
        # Update deliver_department and deliver_faculty based on mapping
        print("Updating deliver_department and deliver_faculty...")
        updated_count = 0
        
        for idx, row in df.iterrows():
            course_code = row['code']
            if course_code in departments_mapping:
                new_faculty, new_department = departments_mapping[course_code]
                
                # Update if different from current values
                if row['deliver_faculty'] != new_faculty or row['deliver_department'] != new_department:
                    df.at[idx, 'deliver_faculty'] = new_faculty
                    df.at[idx, 'deliver_department'] = new_department
                    updated_count += 1
        
        print(f"Updated {updated_count} course entries with new department/faculty info")
        
        # Save the cleaned data
        print(f"Saving cleaned data to {output_file}")
        df.to_csv(output_file, sep='\t', index=False)
        
        print("Cleanup completed successfully!")
        
        # Print some statistics
        print("\n=== Cleanup Statistics ===")
        print(f"Total courses processed: {len(df)}")
        print(f"Courses with updated department/faculty: {updated_count}")
        
        # Show some examples of cleaned types
        print("\n=== Sample type field cleanups ===")
        sample_types = df[df['type'].str.contains(',', na=False)]['type'].head(10)
        for i, type_val in enumerate(sample_types, 1):
            print(f"{i}: {type_val}")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
        raise


def main():
    """Main function"""
    input_file = "input/courses_export_2025-07-19.tsv"
    output_file = "output/courses_export_2025-07-19_cleaned.tsv"
    departments_file = "output/departments-unified.tsv"
    
    print("Course Data Cleanup Script")
    print("=" * 40)
    
    cleanup_course_data(input_file, output_file, departments_file)


if __name__ == "__main__":
    main()
