#!/usr/bin/env python3
"""
Script to extract course information from PDF handbooks using DeepSeek API.

This script:
1. Extracts the second page from all PDFs in a specified directory
2. Converts the PDF pages to plain text
3. Uses DeepSeek API to parse the text into structured course data
4. Outputs the results as TSV format

Usage:
    python pdf_extract_courses.py [--input-dir INPUT_DIR] [--output OUTPUT_FILE]
    
Examples:
    python pdf_extract_courses.py --input-dir assets/handbooks/2025
    python pdf_extract_courses.py --input-dir assets/handbooks/2025 --output courses_extracted.tsv
"""

import argparse
import json
import os
import sys
from pathlib import Path
import csv
from typing import List, Dict, Optional

try:
    import PyPDF2
except ImportError:
    print("Error: PyPDF2 is required. Install it with: pip install PyPDF2")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package is required. Install it with: pip install openai")
    sys.exit(1)


class PDFCourseExtractor:
    """Extract course information from PDF handbooks using DeepSeek API."""
    
    def __init__(self, api_key: str):
        """Initialize the extractor with DeepSeek API key."""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def extract_second_page_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from the second page of a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Optional[str]: Text content of the second page, or None if extraction fails
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF has at least 2 pages
                if len(pdf_reader.pages) < 2:
                    print(f"Warning: {pdf_path} has less than 2 pages, skipping...")
                    return None
                
                # Extract text from second page (index 1)
                second_page = pdf_reader.pages[1]
                text = second_page.extract_text()
                
                if not text.strip():
                    print(f"Warning: No text found on second page of {pdf_path}")
                    return None
                    
                return text.strip()
                
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def parse_courses_with_api(self, text: str, pdf_filename: str) -> List[Dict[str, str]]:
        """
        Parse course information from text using DeepSeek API.
        
        Args:
            text (str): Raw text from PDF page
            pdf_filename (str): Name of the PDF file for context
            
        Returns:
            List[Dict[str, str]]: List of course dictionaries
        """
        system_prompt = """You are an expert at extracting structured course information from university handbook text.

Your task is to analyze the provided text and extract course information in JSON format.

For each course you find, extract:
- course_code: The course code (e.g., "ACCT101", "BUSA200")
- course_name: The full course title/name
- unit: The credit units/points for the course (as string)

Return the data as a JSON object with a "courses" array containing course objects.

Example output format:
{
  "courses": [
    {
      "course_code": "ACCT101",
      "course_name": "Introduction to Accounting",
      "unit": "3"
    },
    {
      "course_code": "ACCT201", 
      "course_name": "Intermediate Accounting",
      "unit": "4"
    }
  ]
}

If no courses are found, return: {"courses": []}

Important guidelines:
- Extract ONLY course information, ignore other content
- Ensure course codes are properly formatted (uppercase letters + numbers)
- Include full course names without truncation
- Convert unit values to strings
- Be precise and accurate with the data extraction"""

        user_prompt = f"""Please extract course information from this text from file "{pdf_filename}":

{text}

Extract all courses with their codes, names, and units. Return as JSON format as specified."""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={
                    'type': 'json_object'
                },
                stream=False
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            courses = result.get("courses", [])
            
            print(f"Extracted {len(courses)} courses from {pdf_filename}")
            return courses
            
        except Exception as e:
            print(f"Error calling DeepSeek API for {pdf_filename}: {e}")
            return []
    
    def process_pdf_directory(self, input_dir: str, output_dir: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Process all PDF files in the specified directory and save individual TSV files.
        
        Args:
            input_dir (str): Path to directory containing PDF files
            output_dir (str): Path to directory where TSV files will be saved
            
        Returns:
            Dict[str, List[Dict[str, str]]]: Dictionary mapping PDF names to their extracted courses
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            print(f"Error: Directory '{input_dir}' does not exist")
            return {}
        
        if not input_path.is_dir():
            print(f"Error: '{input_dir}' is not a directory")
            return {}
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all PDF files
        pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in '{input_dir}'")
            return {}
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        results = {}
        
        for pdf_file in sorted(pdf_files):
            print(f"\nProcessing: {pdf_file.name}")
            
            # Extract text from second page
            text = self.extract_second_page_text(str(pdf_file))
            if not text:
                results[pdf_file.name] = []
                continue
            
            # Parse courses using API
            courses = self.parse_courses_with_api(text, pdf_file.name)
            
            # Add source file information to each course
            for course in courses:
                course['source_file'] = pdf_file.name
            
            results[pdf_file.name] = courses
            
            # Save individual TSV file for this PDF
            if courses:
                # Generate output filename: remove .pdf extension and add .tsv
                output_filename = pdf_file.stem + '.tsv'
                output_filepath = output_path / output_filename
                
                self.save_courses_to_tsv(courses, str(output_filepath))
                print(f"Saved {len(courses)} courses to {output_filename}")
            else:
                print(f"No courses found in {pdf_file.name}")
        
        return results
    
    def save_courses_to_tsv(self, courses: List[Dict[str, str]], output_file: str):
        """
        Save extracted courses to a TSV file.
        
        Args:
            courses (List[Dict[str, str]]): List of course dictionaries
            output_file (str): Output TSV file path
        """
        if not courses:
            print("No courses to save")
            return
        
        # Define TSV columns
        fieldnames = ['course_code', 'course_name', 'unit', 'source_file']
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for course in courses:
                    # Ensure all required fields are present
                    row = {
                        'course_code': course.get('course_code', ''),
                        'course_name': course.get('course_name', ''),
                        'unit': course.get('unit', ''),
                        'source_file': course.get('source_file', '')
                    }
                    writer.writerow(row)
            
            print(f"\nSuccessfully saved {len(courses)} courses to '{output_file}'")
            
        except Exception as e:
            print(f"Error saving to TSV file: {e}")


def main():
    """Main function to run the PDF course extractor."""
    parser = argparse.ArgumentParser(
        description='Extract course information from PDF handbooks using DeepSeek API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python pdf_extract_courses.py --input-dir assets/handbooks/2025
    python pdf_extract_courses.py --input-dir assets/handbooks/2025 --output-dir output/individual_courses

Environment Variables:
    DEEPSEEK_API: DeepSeek API key (required)
        """
    )
    
    parser.add_argument('--input-dir', '-i', 
                       default='assets/handbooks/2025',
                       help='Input directory containing PDF files (default: assets/handbooks/2025)')
    parser.add_argument('--output-dir', '-o',
                       default='output/individual_courses',
                       help='Output directory for individual TSV files (default: output/individual_courses)')
    parser.add_argument('--combined', '-c',
                       help='Optional: Also create a combined TSV file with this name')
    
    args = parser.parse_args()
    
    # Check for DeepSeek API key
    api_key = os.getenv('DEEPSEEK_API')
    if not api_key:
        print("Error: DEEPSEEK_API environment variable is not set")
        print("Please set your DeepSeek API key:")
        print("export DEEPSEEK_API='your-api-key-here'")
        sys.exit(1)
    
    print("=" * 60)
    print("PDF COURSE EXTRACTION WITH DEEPSEEK API")
    print("=" * 60)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    if args.combined:
        print(f"Combined output file: {args.combined}")
    
    # Initialize extractor
    extractor = PDFCourseExtractor(api_key)
    
    try:
        # Process all PDFs and save individual TSV files
        results = extractor.process_pdf_directory(args.input_dir, args.output_dir)
        
        if results:
            # Calculate total courses
            total_courses = sum(len(courses) for courses in results.values())
            
            # Show summary
            print("\n" + "=" * 60)
            print("EXTRACTION SUMMARY")
            print("=" * 60)
            print(f"PDFs processed: {len(results)}")
            print(f"Total courses extracted: {total_courses}")
            
            # Show per-file summary
            print("\nPer-file results:")
            for pdf_name, courses in results.items():
                print(f"  {pdf_name}: {len(courses)} courses")
            
            # Create combined file if requested
            if args.combined:
                all_courses = []
                for courses in results.values():
                    all_courses.extend(courses)
                
                if all_courses:
                    # Create combined output directory if needed
                    combined_path = Path(args.combined)
                    combined_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    extractor.save_courses_to_tsv(all_courses, args.combined)
                    print(f"\nCombined file created: {args.combined} ({len(all_courses)} total courses)")
            
            # Show unique course codes summary
            all_course_codes = set()
            for courses in results.values():
                for course in courses:
                    if course.get('course_code'):
                        all_course_codes.add(course['course_code'])
            
            print(f"\nUnique course codes across all files: {len(all_course_codes)}")
            
            if len(all_course_codes) <= 20:
                print("Course codes found:")
                for code in sorted(all_course_codes):
                    print(f"  - {code}")
            else:
                print("First 20 course codes:")
                for code in sorted(list(all_course_codes)[:20]):
                    print(f"  - {code}")
                print(f"  ... and {len(all_course_codes) - 20} more")
        else:
            print("\nNo courses were extracted from any PDF files.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
