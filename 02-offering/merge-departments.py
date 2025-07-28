#!/usr/bin/env python3
"""
Merge all department TSV files into one unified file.
Keep only the latest record for each unique course code.
"""

import pandas as pd
from pathlib import Path
import glob
import re

def parse_semester_priority(year, semester):
    """
    Create a priority score for sorting records by time.
    Higher score = more recent.
    
    Args:
        year (int): The year
        semester (str): FALL or SPRING
        
    Returns:
        float: Priority score
    """
    # FALL comes after SPRING in the same academic year
    semester_offset = 0.5 if semester == "FALL" else 0.0
    return year + semester_offset

def merge_department_files(input_dir="output", output_filename="departments-unified.tsv"):
    """
    Merge all department TSV files into one unified file.
    
    Args:
        input_dir (str): Directory containing department TSV files
        output_filename (str): Name of output unified file
        
    Returns:
        str: Path to created unified file or None if failed
    """
    try:
        input_path = Path(input_dir)
        
        # Find all department TSV files
        tsv_pattern = str(input_path / "departments-*.tsv")
        tsv_files = glob.glob(tsv_pattern)
        
        if not tsv_files:
            print(f"❌ No department TSV files found in {input_dir}")
            return None
        
        print(f"Found {len(tsv_files)} department TSV files:")
        for file in sorted(tsv_files):
            print(f"  - {Path(file).name}")
        
        # Read and combine all TSV files
        all_dataframes = []
        
        for tsv_file in tsv_files:
            try:
                df = pd.read_csv(tsv_file, sep='\t')
                
                # Ensure required columns exist
                if 'Course Code' not in df.columns:
                    print(f"⚠️  Skipping {tsv_file}: missing 'Course Code' column")
                    continue
                
                if 'Year' not in df.columns or 'Semester' not in df.columns:
                    print(f"⚠️  Skipping {tsv_file}: missing Year/Semester columns")
                    continue
                
                print(f"✅ Read {len(df)} records from {Path(tsv_file).name}")
                all_dataframes.append(df)
                
            except Exception as e:
                print(f"❌ Error reading {tsv_file}: {e}")
                continue
        
        if not all_dataframes:
            print("❌ No valid TSV files could be read")
            return None
        
        # Combine all dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"\n📊 Combined dataset: {len(combined_df)} total records")
        
        # Create priority score for sorting
        combined_df['Priority'] = combined_df.apply(
            lambda row: parse_semester_priority(row['Year'], row['Semester']), 
            axis=1
        )
        
        # Sort by Course Code and Priority (descending to keep latest)
        combined_df = combined_df.sort_values(['Course Code', 'Priority'], ascending=[True, False])
        
        # Keep only the first (latest) record for each course code
        deduplicated_df = combined_df.drop_duplicates(subset=['Course Code'], keep='first')
        
        # Remove the temporary Priority column
        deduplicated_df = deduplicated_df.drop('Priority', axis=1)
        
        # Ensure we have the required output columns
        required_columns = ['Course Code', 'Offering Unit']
        optional_columns = ['Offering Programme', 'Year', 'Semester']
        
        output_columns = required_columns.copy()
        for col in optional_columns:
            if col in deduplicated_df.columns:
                output_columns.append(col)
        
        # Select and reorder columns
        final_df = deduplicated_df[output_columns]
        
        # Sort by Course Code for clean output
        final_df = final_df.sort_values('Course Code')
        
        # Create output file path
        output_path = input_path / output_filename
        
        # Save unified TSV
        final_df.to_csv(output_path, sep='\t', index=False)
        
        print(f"\n✅ Created unified department file: {output_path}")
        print(f"   📈 Total unique courses: {len(final_df)}")
        print(f"   📋 Columns: {list(final_df.columns)}")
        
        # Show some statistics
        if 'Year' in final_df.columns and 'Semester' in final_df.columns:
            year_stats = final_df.groupby(['Year', 'Semester']).size().sort_index()
            print(f"\n📅 Records by semester (latest kept for each course):")
            for (year, semester), count in year_stats.items():
                print(f"   {year} {semester}: {count} courses")
        
        if 'Offering Unit' in final_df.columns:
            unit_stats = final_df['Offering Unit'].value_counts()
            print(f"\n🏢 Top 10 Offering Units:")
            for unit, count in unit_stats.head(10).items():
                print(f"   {unit}: {count} courses")
        
        # Show sample records
        print(f"\n📄 Sample records:")
        print(final_df.head(10).to_string(index=False))
        
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error merging department files: {e}")
        return None

def main():
    """
    Main function
    """
    print("🔄 Merging department TSV files...")
    print("=" * 60)
    
    result = merge_department_files()
    
    if result:
        print(f"\n🎉 Success! Unified department file created: {result}")
    else:
        print(f"\n💥 Failed to create unified department file")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
