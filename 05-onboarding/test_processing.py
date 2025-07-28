#!/usr/bin/env python3
"""
Simple test script to validate course processing functionality
"""

import sys
sys.path.append('.')
from course_onboarding import CourseOnboardingTool

def test_single_course():
    # Test data
    test_course = {
        'course_code': 'GD1003',
        'course_name': 'FOUNDATIONS OF PROGRAMMING FOR GAME DESIGN',
        'course_description': 'This course aims to introduce students to the fundamental concepts and techniques of programming for game design.',
        'unit': '3',
        'prerequisite': 'N/A'
    }
    
    tool = CourseOnboardingTool()
    
    # Test course name capitalization
    print("Testing course name capitalization...")
    proper_name = tool.capitalize_course_name(test_course['course_name'], "llama3.2:3b")
    print(f"Original: {test_course['course_name']}")
    print(f"Capitalized: {proper_name}")
    
    # Test Chinese translation
    print("\nTesting Chinese translation...")
    chinese_name = tool.translate_to_chinese(proper_name, test_course['course_description'], "course name", "llama3.2:3b")
    print(f"English: {proper_name}")
    print(f"Chinese: {chinese_name}")
    
    # Test requirements processing
    print("\nTesting requirements processing...")
    requirements = tool.process_requirements_with_ollama(test_course['prerequisite'], "llama3.2:3b")
    print(f"Original: {test_course['prerequisite']}")
    print(f"Prerequisites: {requirements['prerequisites']}")
    print(f"Exclusions: {requirements['exclusions']}")

if __name__ == "__main__":
    test_single_course()
