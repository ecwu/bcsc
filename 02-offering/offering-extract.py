import pandas as pd
import os
from pathlib import Path

def read_excel_to_dataframes(excel_file_path):
    """
    Read an Excel file and convert all sheets to pandas DataFrames
    
    Args:
        excel_file_path (str): Path to the Excel file
        
    Returns:
        dict: Dictionary where keys are sheet names and values are DataFrames
    """
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel file not found: {excel_file_path}")
    
    try:
        # Convert path to string if it's a Path object
        excel_file_str = str(excel_file_path)
        
        # Determine the appropriate engine based on file extension
        if excel_file_str.endswith('.xlsx'):
            engine = 'openpyxl'
        elif excel_file_str.endswith('.xls'):
            engine = 'xlrd'
        else:
            # Try openpyxl first, then xlrd
            engine = 'openpyxl'
        
        # Read all sheets from the Excel file
        try:
            excel_data = pd.read_excel(excel_file_str, sheet_name=None, engine=engine, header=1)
        except Exception as first_error:
            # If first engine fails, try the other one
            if engine == 'openpyxl':
                print(f"openpyxl failed, trying xlrd: {first_error}")
                excel_data = pd.read_excel(excel_file_str, sheet_name=None, engine='xlrd', header=1)
            else:
                print(f"xlrd failed, trying openpyxl: {first_error}")
                excel_data = pd.read_excel(excel_file_str, sheet_name=None, engine='openpyxl', header=1)
        
        print(f"Successfully read Excel file: {excel_file_str}")
        print(f"Number of sheets found: {len(excel_data)}")
        
        # Clean up DataFrames
        cleaned_data = {}
        for sheet_name, df in excel_data.items():
            # Clean up the DataFrame
            cleaned_df = clean_dataframe(df)
            cleaned_data[sheet_name] = cleaned_df
            
            print(f"\nSheet: '{sheet_name}'")
            print(f"Shape: {cleaned_df.shape}")
            print(f"Columns: {list(cleaned_df.columns)}")
            
        return cleaned_data
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def clean_dataframe(df):
    """
    Clean up the DataFrame by removing empty rows and renaming columns
    
    Args:
        df (pandas.DataFrame): Raw DataFrame from Excel
        
    Returns:
        pandas.DataFrame: Cleaned DataFrame
    """
    # Remove rows that are completely empty
    df_cleaned = df.dropna(how='all')
    
    # If this looks like the course timetable, apply specific column names
    if df_cleaned.shape[1] >= 12:
        expected_columns = [
            'Course Code',
            'Course Title & Session', 
            'Offering Unit',
            'Offering Programme',
            'Units',
            'Curriculum Type',
            'Elective Type',
            'Teachers',
            'Class Schedule',
            'Hours',
            'Classroom',
            'Requirements',
            'Remarks'
        ]
        
        # Rename columns with proper names
        column_mapping = {}
        for i, col_name in enumerate(expected_columns):
            if i < len(df_cleaned.columns):
                column_mapping[df_cleaned.columns[i]] = col_name
        
        df_cleaned = df_cleaned.rename(columns=column_mapping)
    
    return df_cleaned

def analyze_course_data(df):
    """
    Perform basic analysis on the course DataFrame
    
    Args:
        df (pandas.DataFrame): Course DataFrame
        
    Returns:
        dict: Analysis results
    """
    analysis = {
        'total_courses': len(df),
        'unique_course_codes': df['Course Code'].nunique(),
        'offering_units': df['Offering Unit'].value_counts(),
        'curriculum_types': df['Curriculum Type'].value_counts(),
        'teachers_count': df['Teachers'].nunique(),
        'average_units': df['Units'].mean(),
        'total_hours': df['Hours'].sum()
    }
    
    return analysis

def get_courses_by_unit(df, unit):
    """
    Filter courses by offering unit
    
    Args:
        df (pandas.DataFrame): Course DataFrame
        unit (str): Offering unit (e.g., 'FBM', 'FST', etc.)
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    return df[df['Offering Unit'] == unit]

def get_courses_by_code_pattern(df, pattern):
    """
    Filter courses by course code pattern
    
    Args:
        df (pandas.DataFrame): Course DataFrame
        pattern (str): Pattern to match in course codes
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    return df[df['Course Code'].str.contains(pattern, na=False)]

def extract_year_semester_from_filename(filename):
    """
    Extract year and semester from filename
    
    Args:
        filename (str): Excel filename
        
    Returns:
        tuple: (year, semester) or (None, None) if not found
    """
    import re
    
    # Pattern to match AY2024-25 format
    year_pattern = r'AY(\d{4})-(\d{2})'
    year_match = re.search(year_pattern, filename)
    
    # Alternative pattern for AY2022_23 format
    if not year_match:
        year_pattern_alt = r'AY(\d{4})_(\d{2})'
        year_match = re.search(year_pattern_alt, filename)
    
    # Pattern to match semester
    semester_pattern = r'Semester[_\s](\d+)'
    semester_match = re.search(semester_pattern, filename)
    
    if year_match and semester_match:
        start_year = year_match.group(1)
        semester = semester_match.group(1)
        return start_year, semester
    
    return None, None

def process_excel_to_offering_csv(excel_file_path, output_dir="output"):
    """
    Process an Excel file and create a CSV file with course offerings
    
    Args:
        excel_file_path (str): Path to the Excel file
        output_dir (str): Directory to save output CSV files
        
    Returns:
        str: Path to created CSV file or None if failed
    """
    try:
        # Read the Excel file
        dataframes = read_excel_to_dataframes(excel_file_path)
        
        if not dataframes:
            print(f"Failed to read Excel file: {excel_file_path}")
            return None
        
        # Find the main course sheet
        main_sheet = None
        course_df = None
        for sheet_name, df in dataframes.items():
            if ('Course List' in sheet_name or 'Timetable' in sheet_name or 
                'Export' in sheet_name or 'Semester' in sheet_name):
                main_sheet = sheet_name
                course_df = df
                break
        
        # If still not found, use the first (and likely only) sheet
        if course_df is None and dataframes:
            main_sheet = list(dataframes.keys())[0]
            course_df = list(dataframes.values())[0]
        
        if course_df is None:
            print(f"No course data sheet found in {excel_file_path}")
            return None
        
        # Extract year and semester from filename
        filename = Path(excel_file_path).name
        year, semester = extract_year_semester_from_filename(filename)
        
        if not year or not semester:
            print(f"Could not extract year/semester from filename: {filename}")
            return None
        
        # Extract course_code and lecturer_name columns
        if 'Course Code' not in course_df.columns or 'Teachers' not in course_df.columns:
            print(f"Required columns not found in {excel_file_path}")
            print(f"Available columns: {list(course_df.columns)}")
            return None
        
        # Create offering DataFrame with required columns
        offering_df = course_df[['Course Code', 'Teachers']].copy()
        offering_df = offering_df.rename(columns={
            'Course Code': 'course_code',
            'Teachers': 'lecturer_name'
        })
        
        # Remove rows with missing course_code or lecturer_name
        offering_df = offering_df.dropna(subset=['course_code', 'lecturer_name'])
        
        # Filter out empty lecturer names
        offering_df = offering_df[offering_df['lecturer_name'].str.strip() != '']
        
        # Clean lecturer names - remove prefixes like "Course Convener:", "Instructor:", etc.
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.replace(r'^Course Convener:\s*', '', regex=True)
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.replace(r'^Instructor:\s*', '', regex=True)
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.replace(r'^Teacher:\s*', '', regex=True)
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.replace(r'^Lecturer:\s*', '', regex=True)
        
        # Remove any remaining empty strings after cleaning
        offering_df = offering_df[offering_df['lecturer_name'].str.strip() != '']
        
        # Map semester numbers to names
        semester_map = {'1': 'FALL', '2': 'SPRING'}
        semester_name = semester_map.get(semester, semester)
        
        # Add year and semester columns
        offering_df['year'] = year
        offering_df['semester'] = semester_name
        
        # Reorder columns to desired order: course_code, year, semester, lecturer_name
        offering_df = offering_df[['course_code', 'year', 'semester', 'lecturer_name']]
        
        # Drop duplicate course_code & lecturer_name combinations
        offering_df = offering_df.drop_duplicates(subset=['course_code', 'lecturer_name'])
        
        # Split lecturer_name by '&' and explode into separate rows
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.split('&')
        offering_df = offering_df.explode('lecturer_name')
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.strip()
        
        # Clean lecturer names again after splitting (in case prefixes are in individual parts)
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.replace(r'^Course Convener:\s*', '', regex=True)
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.replace(r'^Instructor:\s*', '', regex=True)
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.replace(r'^Teacher:\s*', '', regex=True)
        offering_df['lecturer_name'] = offering_df['lecturer_name'].str.replace(r'^Lecturer:\s*', '', regex=True)
        
        # Remove any remaining empty lecturer names or invalid entries
        offering_df = offering_df[offering_df['lecturer_name'].str.len() > 0]
        offering_df = offering_df[~offering_df['lecturer_name'].str.startswith('TBC', na=False)]
        offering_df = offering_df[~offering_df['lecturer_name'].str.startswith('TBA', na=False)]
        
        # Create output directory relative to script location if it doesn't exist
        script_dir = Path(__file__).parent
        output_path = script_dir / output_dir
        output_path.mkdir(exist_ok=True)
        
        # Create output filename
        output_filename = f"offering-{year}-{semester_name}.csv"
        output_file_path = output_path / output_filename
        
        # Save as CSV
        offering_df.to_csv(output_file_path, index=False)
        
        print(f"✅ Created: {output_file_path}")
        print(f"   Records: {len(offering_df)}")
        print(f"   Unique courses: {offering_df['course_code'].nunique()}")
        print(f"   Unique lecturers: {offering_df['lecturer_name'].nunique()}")
        
        return str(output_file_path)
        
    except Exception as e:
        print(f"❌ Error processing {excel_file_path}: {e}")
        return None

def process_excel_to_department_tsv(excel_file_path, output_dir="output"):
    """
    Process an Excel file and create a TSV file with course code and department/faculty information
    
    Args:
        excel_file_path (str): Path to the Excel file
        output_dir (str): Directory to save output TSV files
        
    Returns:
        str: Path to created TSV file or None if failed
    """
    try:
        # Read the Excel file
        dataframes = read_excel_to_dataframes(excel_file_path)
        
        if not dataframes:
            print(f"Failed to read Excel file: {excel_file_path}")
            return None
        
        # Find the main course sheet
        main_sheet = None
        course_df = None
        for sheet_name, df in dataframes.items():
            if ('Course List' in sheet_name or 'Timetable' in sheet_name or 
                'Export' in sheet_name or 'Semester' in sheet_name):
                main_sheet = sheet_name
                course_df = df
                break
        
        # If still not found, use the first (and likely only) sheet
        if course_df is None and dataframes:
            main_sheet = list(dataframes.keys())[0]
            course_df = list(dataframes.values())[0]
        
        if course_df is None:
            print(f"No course data sheet found in {excel_file_path}")
            return None
        
        # Extract year and semester from filename
        filename = Path(excel_file_path).name
        year, semester = extract_year_semester_from_filename(filename)
        
        if not year or not semester:
            print(f"Could not extract year/semester from filename: {filename}")
            return None
        
        # Check for required columns
        required_columns = ['Course Code']
        department_columns = []
        
        # Look for department/faculty related columns
        if 'Offering Unit' in course_df.columns:
            department_columns.append('Offering Unit')
        if 'Offering Programme' in course_df.columns:
            department_columns.append('Offering Programme')
        
        if not department_columns:
            print(f"No department/faculty columns found in {excel_file_path}")
            print(f"Available columns: {list(course_df.columns)}")
            return None
        
        # Create department DataFrame
        columns_to_extract = ['Course Code'] + department_columns
        dept_df = course_df[columns_to_extract].copy()
        
        # Remove rows with missing course code
        dept_df = dept_df.dropna(subset=['Course Code'])
        
        # Map semester numbers to names
        semester_map = {'1': 'FALL', '2': 'SPRING'}
        semester_name = semester_map.get(semester, semester)
        
        # Add year and semester columns
        dept_df.insert(1, 'Year', year)
        dept_df.insert(2, 'Semester', semester_name)
        
        # Remove duplicates based on all columns
        dept_df = dept_df.drop_duplicates()
        
        # Create output directory relative to script location if it doesn't exist
        script_dir = Path(__file__).parent
        output_path = script_dir / output_dir
        output_path.mkdir(exist_ok=True)
        
        # Create output filename
        output_filename = f"departments-{year}-{semester_name}.tsv"
        output_file_path = output_path / output_filename
        
        # Save as TSV
        dept_df.to_csv(output_file_path, sep='\t', index=False)
        
        print(f"✅ Created: {output_file_path}")
        print(f"   Records: {len(dept_df)}")
        print(f"   Unique courses: {dept_df['Course Code'].nunique()}")
        print(f"   Columns: {list(dept_df.columns)}")
        
        return str(output_file_path)
        
    except Exception as e:
        print(f"❌ Error processing {excel_file_path}: {e}")
        return None

def process_all_excel_files_departments():
    """
    Process all Excel files and create TSV files with department information
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    excel_files = [
        "input/Course List and Timetable_Semester 1 of AY2025-26_20250712.xls",
        "input/Course List and Timetable (Semester 2 of AY2021-22)_20220113.xls",
        "input/Course List and Timetable_Semester 1 of AY2023-24.xlsx",
        "input/Course List and Timetable_Semester 1 of AY2024-25_20240711.xlsx",
        "input/Course List and Timetable_Semester 2 of AY2023-24_20240219.xlsx",
        "input/Course List and Timetable_Semester 2 of AY2024-25_20241231.xls",
        "input/Full_Course_List_and_Timetable_Semester_2_of_AY2022_23_20230214.xls"
    ]
    
    print(f"Processing {len(excel_files)} Excel files for department information...")
    
    successful = []
    failed = []
    
    for excel_file in excel_files:
        print(f"\n{'='*60}")
        print(f"Processing: {excel_file}")
        print(f"{'='*60}")
        
        # Convert to absolute path
        excel_path = script_dir / excel_file
        
        try:
            result = process_excel_to_department_tsv(str(excel_path))
            if result:
                successful.append(result)
            else:
                failed.append(excel_file)
        except Exception as e:
            print(f"❌ Error: {e}")
            failed.append(excel_file)
    
    print(f"\n{'='*80}")
    print(f"DEPARTMENT PROCESSING SUMMARY")
    print(f"{'='*80}")
    print(f"Total files: {len(excel_files)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print(f"\n✅ Successfully created department TSV files:")
        for file_path in successful:
            print(f"   - {file_path}")
    
    if failed:
        print(f"\n❌ Failed to process:")
        for file_path in failed:
            print(f"   - {file_path}")
    
    return successful, failed

def process_all_excel_files():
    """
    Process all Excel files and create CSV offerings
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    excel_files = [
        "input/Course List and Timetable_Semester 1 of AY2025-26_20250712.xls",
        "input/Course List and Timetable (Semester 2 of AY2021-22)_20220113.xls",
        "input/Course List and Timetable_Semester 1 of AY2023-24.xlsx",
        "input/Course List and Timetable_Semester 1 of AY2024-25_20240711.xlsx",
        "input/Course List and Timetable_Semester 2 of AY2023-24_20240219.xlsx",
        "input/Course List and Timetable_Semester 2 of AY2024-25_20241231.xls",
        "input/Full_Course_List_and_Timetable_Semester_2_of_AY2022_23_20230214.xls"
    ]
    
    print(f"Processing {len(excel_files)} Excel files...")
    
    successful = []
    failed = []
    
    for excel_file in excel_files:
        print(f"\n{'='*60}")
        print(f"Processing: {excel_file}")
        print(f"{'='*60}")
        
        # Convert to absolute path
        excel_path = script_dir / excel_file
        
        try:
            result = process_excel_to_offering_csv(str(excel_path))
            if result:
                successful.append(result)
            else:
                failed.append(excel_file)
        except Exception as e:
            print(f"❌ Error: {e}")
            failed.append(excel_file)
    
    print(f"\n{'='*80}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*80}")
    print(f"Total files: {len(excel_files)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print(f"\n✅ Successfully created CSV files:")
        for file_path in successful:
            print(f"   - {file_path}")
    
    if failed:
        print(f"\n❌ Failed to process:")
        for file_path in failed:
            print(f"   - {file_path}")
    
    return successful, failed

def test_single_file(excel_file):
    """
    Test parsing a single Excel file
    
    Args:
        excel_file (str): Path to the Excel file (can be relative or absolute)
        
    Returns:
        dict: DataFrames or None if failed
    """
    print(f"\n{'='*80}")
    print(f"TESTING FILE: {excel_file}")
    print(f"{'='*80}")
    
    # Convert to absolute path if it's relative
    excel_path = Path(excel_file)
    if not excel_path.is_absolute():
        current_dir = Path(__file__).parent
        excel_path = current_dir / excel_file
    
    print(f"Full path: {excel_path}")
    
    # Read Excel file and convert to DataFrames
    dataframes = read_excel_to_dataframes(str(excel_path))
    
    if dataframes:
        # Display basic information about each DataFrame
        for sheet_name, df in dataframes.items():
            print(f"\nSheet: {sheet_name}")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Show first few rows
            print(f"\nFirst 3 rows:")
            print(df.head(3).to_string())
            
        # Additional utility functions for the course data
        main_sheet = None
        for sheet_name in dataframes.keys():
            if 'Course List' in sheet_name or 'Timetable' in sheet_name:
                main_sheet = sheet_name
                break
        
        if main_sheet:
            course_df = dataframes[main_sheet]
            print(f"\n--- SUMMARY STATISTICS for '{main_sheet}' ---")
            print(f"Total courses/sessions: {len(course_df)}")
            print(f"Unique course codes: {course_df['Course Code'].nunique()}")
            
            if 'Offering Unit' in course_df.columns:
                print(f"Offering units: {sorted(course_df['Offering Unit'].unique())}")
            if 'Curriculum Type' in course_df.columns:
                print(f"Curriculum types: {sorted(course_df['Curriculum Type'].unique())}")
            
            # Show some sample course codes
            print(f"Sample course codes: {list(course_df['Course Code'].unique()[:5])}")
        
        return dataframes
    else:
        print("❌ FAILED to read Excel file")
        return None

def test_all_files():
    """
    Test parsing all Excel files in the input folder
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    excel_files = [
        "input/Course List and Timetable_Semester 1 of AY2025-26_20250712.xls",
        "input/Course List and Timetable (Semester 2 of AY2021-22)_20220113.xls",
        "input/Course List and Timetable_Semester 1 of AY2023-24.xlsx",
        "input/Course List and Timetable_Semester 1 of AY2024-25_20240711.xlsx",
        "input/Course List and Timetable_Semester 2 of AY2023-24_20240219.xlsx",
        "input/Course List and Timetable_Semester 2 of AY2024-25_20241231.xls",
        "input/Full_Course_List_and_Timetable_Semester_2_of_AY2022_23_20230214.xls"
    ]
    
    results = {}
    successful = 0
    failed = 0
    
    for excel_file in excel_files:
        try:
            # Convert to absolute path
            excel_path = script_dir / excel_file
            result = test_single_file(str(excel_path))
            if result:
                results[excel_file] = result
                successful += 1
                print("✅ SUCCESS")
            else:
                failed += 1
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"Total files tested: {len(excel_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    return results

def main():
    """
    Main function - choose between testing files, processing to CSV, or extracting departments
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--process":
        # Process all Excel files to CSV
        print("Processing all Excel files to CSV format...")
        return process_all_excel_files()
    elif len(sys.argv) > 1 and sys.argv[1] == "--departments":
        # Process all Excel files to extract department information
        print("Processing all Excel files to extract department information...")
        return process_all_excel_files_departments()
    else:
        # Test all Excel files (default behavior)
        print("Testing all Excel files...")
        return test_all_files()

if __name__ == "__main__":
    dataframes = main()