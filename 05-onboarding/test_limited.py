#!/usr/bin/env python3
"""
Test script to process just the first few missing courses
"""

import sys
sys.path.append('.')
from course_onboarding import CourseOnboardingTool

def test_limited_processing():
    tool = CourseOnboardingTool()
    
    # Find missing courses
    missing_codes, missing_details = tool.find_missing_courses(
        "input/courses_export_2025-07-19.tsv", 
        "output/20250702.tsv"
    )
    
    if missing_details:
        # Process only the first 3 courses for testing
        limited_details = missing_details[:3]
        print(f"\nProcessing first {len(limited_details)} courses for testing...")
        
        processed_courses = tool.process_missing_courses(limited_details, "llama3.2:3b")
        
        # Save results
        tool.save_to_tsv(processed_courses, "test_limited_onboarding.tsv")
        
        print(f"\n✓ Test completed! Processed {len(processed_courses)} courses")
        print("Results saved to test_limited_onboarding.tsv")
    else:
        print("No missing courses found!")

if __name__ == "__main__":
    test_limited_processing()
