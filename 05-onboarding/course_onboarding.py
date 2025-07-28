#!/usr/bin/env python3
"""
Course Onboarding Script

This script finds courses missing in the input file but present in the output file,
then converts them into the proper TSV format with all required fields.
Features:
1. Finds missing courses between input and output files
2. Converts course names to proper capitalization using Ollama
3. Translates English names and descriptions to Chinese using Ollama
4. Generates properly formatted TSV with all required fields

Usage:
    python course_onboarding.py <input_file> <output_file> [--ollama-host HOST] [--output-tsv OUTPUT_TSV]
"""

import argparse
import csv
import sys
import requests
from pathlib import Path
from typing import Dict, List, Set, Optional
import time
import re
import xml.etree.ElementTree as ElementTree


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host.rstrip('/')
        self.session = requests.Session()
        
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.RequestException:
            return []
    
    def generate(self, model: str, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Generate text using Ollama model"""
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistency
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                }
                
                response = self.session.post(
                    f"{self.host}/api/generate",
                    json=payload,
                    timeout=120  # Increased timeout for large models
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '').strip()
                else:
                    print(f"Ollama API error: {response.status_code} - {response.text}")
                    
            except requests.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                    
        return None


class CourseOnboardingTool:
    """Main class for course onboarding functionality"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama = OllamaClient(ollama_host)
        self.required_headers = [
            'code', 'name_en', 'name_cn', 'type', 'units', 
            'deliver_department', 'deliver_faculty', 'prerequisites', 
            'exclusions', 'description', 'is_visible'
        ]
        
    def load_course_codes(self, file_path: str, code_column: str) -> Set[str]:
        """Load course codes from TSV file"""
        course_codes = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')
                for row in reader:
                    course_code = row[code_column].strip()
                    if course_code:
                        course_codes.add(course_code)
        except (FileNotFoundError, csv.Error, UnicodeDecodeError) as e:
            print(f"Error reading {file_path}: {e}")
            sys.exit(1)
        return course_codes
    
    def load_course_details(self, file_path: str, course_codes: Set[str], code_column: str) -> List[Dict]:
        """Load detailed course information for specific course codes"""
        course_details = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')
                for row in reader:
                    if row[code_column].strip() in course_codes:
                        course_details.append(row)
        except (FileNotFoundError, csv.Error, UnicodeDecodeError) as e:
            print(f"Error reading course details from {file_path}: {e}")
            sys.exit(1)
        return course_details
    
    def find_missing_courses(self, input_file: str, output_file: str) -> tuple[Set[str], List[Dict]]:
        """Find courses missing in input but present in output"""
        print(f"Loading courses from input file: {input_file}")
        input_codes = self.load_course_codes(input_file, 'code')
        print(f"Found {len(input_codes)} courses in input file")
        
        print(f"Loading courses from output file: {output_file}")
        output_codes = self.load_course_codes(output_file, 'course_code')
        print(f"Found {len(output_codes)} courses in output file")
        
        missing_codes = output_codes - input_codes
        print(f"Found {len(missing_codes)} missing courses")
        
        if missing_codes:
            missing_details = self.load_course_details(output_file, missing_codes, 'course_code')
            return missing_codes, missing_details
        
        return set(), []
    
    def capitalize_course_name(self, course_name: str, model: str = "qwen3:30b-a3b") -> str:
        """Use Ollama to properly capitalize course names"""
        if not course_name:
            return ""
            
        prompt = f"""Convert this all-caps course name to proper title case following academic standards:

Input: "{course_name}"

Rules:
- Use title case (capitalize first letter of major words)
- Keep articles, prepositions, and conjunctions lowercase unless they're the first word
- Preserve acronyms like "AI", "VR", "3D", "API", "HTML", "CSS", "SQL", etc.
- Academic terms should be properly capitalized
- Roman numerals should remain as "I", "II", etc.

Return only the properly formatted course name, no explanations."""

        result = self.ollama.generate(model, prompt)
        if result:
            # Clean up the result - remove quotes and extra whitespace
            result = result.strip().strip('"').strip("'")
            return result
        else:
            # Fallback: basic title case
            return course_name.title()
    
    def translate_to_chinese(self, text: str, description: str = "", text_type: str = "course name", model: str = "qwen3:30b-a3b") -> str:
        """Use Ollama to translate English text to Chinese"""
        if not text:
            return ""
            
        if text_type == "course name":
            prompt = f"""Task: Translate to Chinese

English: {text}
Context: {description}

Output only the Chinese translation (no explanations):"""
        else:  # course description
            prompt = f"""Translate this English course description to Chinese (Simplified Chinese characters):

English: "{text}"

Requirements:
- Provide a natural, academic Chinese translation
- Use terminology commonly used in Chinese universities and course catalogs
- Maintain the formal tone and structure
- Keep technical terms accurate
- Return only the Chinese translation, no explanations or additional text

Chinese translation:"""

        result = self.ollama.generate(model, prompt)
        if result:
            # Clean up the result more aggressively
            result = result.strip().strip('"').strip("'")
            
            # Handle cases where the model returns multiple options or extra text
            # Take the first line if there are multiple lines
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('或') and not line.startswith('这'):
                    # Skip lines starting with "或" (or) or "这" (this) which are likely explanations
                    result = line.strip('"').strip("'")
                    break
            
            # Remove common prefixes that models might add
            prefixes_to_remove = ['中文：', '中文:', '翻译：', '翻译:', 'Chinese:', 'Translation:']
            for prefix in prefixes_to_remove:
                if result.startswith(prefix):
                    result = result[len(prefix):].strip()
            
            return result
        else:
            return f"{text} (翻译待完成)"  # Fallback
    
    def extract_department_from_code(self, course_code: str) -> str:
        """Extract department from course code (e.g., 'GD1003' -> 'GD')"""
        match = re.match(r'^([A-Z]+)', course_code)
        return match.group(1) if match else ""
    
    def process_requirements_with_ollama(self, text: str, model: str = "qwen3:30b-a3b") -> Dict[str, str]:
        """Process enrollment requirements using Ollama API."""
        if not text or text.strip() in ['N/A', '']:
            return {"prerequisites": "", "exclusions": ""}

        try:
            prompt_instruction = """/no_think 将文本化课程前置要求转换为特定的格式：
例子：
1. 
<original>未曾修读过GCIT1013 同时 未曾修读过COMP1013 同时 未曾修读过STAT2043 同时 未曾修读过COMP3153</original>
<prerequisites></prerequisites>
<exclusions>GCIT1013 AND COMP1013 AND STAT2043 AND COMP3153</exclusions>

2. 
<original>(需修读过ACCT2003 或者 ACCT2043) 同时 未曾修读过ACCT2053 同时 专业需为ACCT</original>
<prerequisites>ACCT2003 OR ACCT2043</prerequisites>
<exclusions>ACCT2053 AND Student Major in ACCT</exclusions>
	

3. 
<original>需修读过ACCT3003</original>
<prerequisites>ACCT3003</prerequisites>
<exclusions></exclusions>

You should only output the XML part, without any additional text or explanation. Do not repeat the original text in your output.
<original>{text}</original>"""
            
            response = self.ollama.generate(model, prompt_instruction.format(text=text))
            
            if not response:
                print("    Warning: No response from Ollama for requirements processing")
                return {"prerequisites": "", "exclusions": ""}
            
            # Get raw Ollama response
            raw_response = response.strip()
            print(f"    Raw requirements response: {raw_response[:100]}..." if len(raw_response) > 100 else f"    Raw requirements response: {raw_response}")
            
            # Extract prerequisites and exclusions using string operations
            try:
                # Find the content between tags
                prereq_start = raw_response.find('<prerequisites>') + len('<prerequisites>')
                prereq_end = raw_response.find('</prerequisites>')
                excl_start = raw_response.find('<exclusions>') + len('<exclusions>')
                excl_end = raw_response.find('</exclusions>')
                
                if prereq_start == -1 or prereq_end == -1 or excl_start == -1 or excl_end == -1:
                    print(f"    Warning: Missing required tags in response: {raw_response}")
                    return {"prerequisites": "", "exclusions": ""}
                
                prerequisites = raw_response[prereq_start:prereq_end].strip()
                exclusions = raw_response[excl_start:excl_end].strip()
                
                # Construct clean XML
                xml_text = f"<root><prerequisites>{prerequisites}</prerequisites><exclusions>{exclusions}</exclusions></root>"
                print(f"    Clean XML: {xml_text}")
            except (ValueError, IndexError) as e:
                print(f"    Error extracting content: {e}")
                return {"prerequisites": "", "exclusions": ""}
            
            # Parse clean XML response
            try:
                root = ElementTree.fromstring(xml_text)
                
                # Find prerequisites and exclusions, accounting for possible root wrapping
                prereq_elem = root.find('.//prerequisites')
                excl_elem = root.find('.//exclusions')
                
                result = {
                    "prerequisites": prereq_elem.text or "" if prereq_elem is not None else "",
                    "exclusions": excl_elem.text or "" if excl_elem is not None else ""
                }
                return result
            except ElementTree.ParseError as e:
                print(f"    Error parsing XML: {e}")
                return {"prerequisites": "", "exclusions": ""}
            
        except (requests.RequestException, ElementTree.ParseError) as e:
            print(f"    Error processing requirements: {e}")
            return {"prerequisites": "", "exclusions": ""}
    
    def process_missing_courses(self, missing_details: List[Dict], model: str = "qwen3:30b-a3b") -> List[Dict]:
        """Process missing courses to create proper TSV format"""
        processed_courses = []
        
        print(f"\nProcessing {len(missing_details)} missing courses...")
        
        for i, course in enumerate(missing_details, 1):
            print(f"Processing course {i}/{len(missing_details)}: {course['course_code']}")
            
            # Extract basic info
            course_code = course['course_code']
            original_name = course.get('course_name', '')
            original_description = course.get('course_description', '')
            units = course.get('unit', '3')  # Default to 3 units
            prerequisites = course.get('prerequisite', 'N/A')
            
            # Process course name
            print("  - Capitalizing course name...")
            proper_name = self.capitalize_course_name(original_name, model)
            
            # Translate to Chinese
            print("  - Translating course name to Chinese...")
            chinese_name = self.translate_to_chinese(proper_name, original_description, "course name", model)
            
            # Process prerequisites and exclusions
            print("  - Processing prerequisites and exclusions...")
            requirements = self.process_requirements_with_ollama(prerequisites, model)
            processed_prerequisites = requirements["prerequisites"]
            processed_exclusions = requirements["exclusions"]
            
            # Extract department from course code
            department = self.extract_department_from_code(course_code)
            
            # Create processed course entry
            processed_course = {
                'code': course_code,
                'name_en': proper_name,
                'name_cn': chinese_name,
                'type': 'UNK(UNK)',
                'units': str(units),
                'deliver_department': department,
                'deliver_faculty': '',  # To be filled manually
                'prerequisites': processed_prerequisites,
                'exclusions': processed_exclusions,
                'description': original_description,  # Keep original English description
                'is_visible': 'true'
            }
            
            processed_courses.append(processed_course)
            
            # Add a small delay to be respectful to the API
            time.sleep(0.2)  # Reduced delay since we're using fewer requests now
            
            print(f"  ✓ Completed: {proper_name} -> {chinese_name}")
            if processed_prerequisites:
                print(f"    Prerequisites: {processed_prerequisites}")
            if processed_exclusions:
                print(f"    Exclusions: {processed_exclusions}")
        
        return processed_courses
    
    def save_to_tsv(self, courses: List[Dict], output_file: str):
        """Save processed courses to TSV file"""
        print(f"\nSaving {len(courses)} courses to {output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.required_headers, delimiter='\t')
                writer.writeheader()
                writer.writerows(courses)
            print(f"Successfully saved to {output_file}")
        except (IOError, OSError, csv.Error) as e:
            print(f"Error saving to {output_file}: {e}")
            sys.exit(1)
    
    def run(self, input_file: str, output_file: str, output_tsv: str, model: str = "qwen3:30b-a3b"):
        """Main execution method"""
        print("=" * 60)
        print("COURSE ONBOARDING TOOL")
        print("=" * 60)
        
        # Check if files exist
        if not Path(input_file).exists():
            print(f"Error: Input file '{input_file}' does not exist")
            sys.exit(1)
            
        if not Path(output_file).exists():
            print(f"Error: Output file '{output_file}' does not exist")
            sys.exit(1)
        
        # Check Ollama availability
        print("Checking Ollama service...")
        if not self.ollama.is_available():
            print("Error: Ollama service is not available. Please make sure Ollama is running.")
            print("You can start Ollama by running: ollama serve")
            sys.exit(1)
        
        # Check if model is available
        available_models = self.ollama.list_models()
        if model not in available_models:
            print(f"Warning: Model '{model}' not found. Available models: {available_models}")
            if available_models:
                model = available_models[0]
                print(f"Using model: {model}")
            else:
                print("No models available. Please install a model first.")
                print("Example: ollama pull qwen3:30b-a3b")
                sys.exit(1)
        else:
            print(f"Using model: {model}")
        
        # Find missing courses
        missing_codes, missing_details = self.find_missing_courses(input_file, output_file)
        
        if not missing_details:
            print("\n✓ No missing courses found! All courses in output file are present in input file.")
            return
        
        print(f"\nMissing courses: {', '.join(sorted(missing_codes))}")
        
        # Process missing courses
        processed_courses = self.process_missing_courses(missing_details, model)
        
        # Save to TSV
        self.save_to_tsv(processed_courses, output_tsv)
        
        print("\n" + "=" * 60)
        print("ONBOARDING COMPLETE")
        print("=" * 60)
        print(f"Processed {len(processed_courses)} courses")
        print(f"Output saved to: {output_tsv}")
        print("\nNext steps:")
        print("1. Review the generated TSV file")
        print("2. Fill in the 'deliver_faculty' field manually")
        print("3. Adjust any translations or course names as needed")
        print("4. Import the courses into your system")


def main():
    parser = argparse.ArgumentParser(
        description='Course onboarding tool with Ollama integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python course_onboarding.py input/courses_export_2025-07-19.tsv output/20250702.tsv
    python course_onboarding.py input.tsv output.tsv --ollama-host http://192.168.1.100:11434
    python course_onboarding.py input.tsv output.tsv --output-tsv new_courses.tsv --model qwen2.5:latest
        """
    )
    
    parser.add_argument('input_file', help='Input TSV file (with "code" column)')
    parser.add_argument('output_file', help='Output TSV file (with "course_code" column)')
    parser.add_argument('--ollama-host', default='http://localhost:11434',
                       help='Ollama API host (default: http://localhost:11434)')
    parser.add_argument('--output-tsv', default='onboarding_courses.tsv',
                       help='Output TSV file for processed courses (default: onboarding_courses.tsv)')
    parser.add_argument('--model', default='qwen3:30b-a3b',
                       help='Ollama model to use (default: qwen3:30b-a3b)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create onboarding tool
    tool = CourseOnboardingTool(args.ollama_host)
    
    # Run the tool
    tool.run(args.input_file, args.output_file, args.output_tsv, args.model)


if __name__ == "__main__":
    main()
