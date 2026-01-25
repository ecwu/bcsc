import requests
import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime


def get_current_date():
    """
    Get current date in ISO format

    Returns:
        str: Current date in ISO format (YYYY-MM-DD)
    """
    return datetime.now().strftime("%Y-%m-%d")


def merge_teacher_names(name: str, name_en: str) -> str:
    """
    Merge Chinese and English names, intelligently handling overlaps.

    Strategy:
    1. If names are identical → use once
    2. If one tokenized name is a subset of the other → use longer name
    3. Otherwise → concatenate both

    Examples:
        "Mehrubon MAVLONI" + "Michael Mehrubon MAVLONI" → "Michael Mehrubon MAVLONI"
        "Smith" + "John Smith" → "John Smith"
        "Zhang San" + "John Zhang" → "Zhang San John Zhang"

    Args:
        name: Chinese name (may contain English)
        name_en: English name

    Returns:
        Merged full name
    """
    if not name or not name_en:
        return name or name_en

    name_clean = name.strip()
    name_en_clean = name_en.strip()

    # Case 1: Exact match
    if name_clean.lower() == name_en_clean.lower():
        return name_clean  # Use the original casing

    # Case 2: Check for token subset (overlap detection)
    name_tokens = [t.lower() for t in name_clean.split()]
    name_en_tokens = [t.lower() for t in name_en_clean.split()]

    name_set = set(name_tokens)
    name_en_set = set(name_en_tokens)

    # Check if one is subset of the other
    if name_set.issubset(name_en_set):
        # name is subset of name_en → use name_en (longer)
        return name_en_clean
    elif name_en_set.issubset(name_set):
        # name_en is subset of name → use name (longer)
        return name_clean

    # Case 3: No overlap → concatenate
    return f"{name_clean} {name_en_clean}"


def fetch_all_teachers():
    """
    Fetch all teacher information from the BNBU staff API

    Returns:
        list: List of teacher dictionaries
    """
    base_url = "https://staff.bnbu.edu.cn/teacher/teacher/list?access-token=&page={}&pageSize=500&key=&lang=en"
    page = 0
    teachers = []

    print("Fetching teacher data from BNBU API...")

    while True:
        print(f"Fetching page {page + 1}...")
        response = requests.get(base_url.format(page))
        response.raise_for_status()  # Check if request was successful
        data = response.json()

        total = data.get("data", {}).get("total", 0)
        print(f"Total teachers: {total}")
        print(f"Page {page + 1}/{(total + 499) // 500}")

        page_teachers = data.get("data", {}).get("data", [])
        if not page_teachers:
            break

        teachers.extend(page_teachers)
        page += 1

        if len(teachers) >= total:
            break

    teachers.sort(key=lambda x: x.get("id"))  # Sort teacher list by ID
    print(f"Successfully fetched {len(teachers)} teachers")

    return teachers


def save_teachers_json(teachers, output_dir="output"):
    """
    Save teacher data as JSON file with date in filename

    Args:
        teachers (list): List of teacher dictionaries
        output_dir (str): Directory to save the JSON file

    Returns:
        str: Path to saved JSON file
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    date = get_current_date()
    json_file_path = output_path / f"teachers-{date}.json"

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(teachers, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved teacher data to: {json_file_path}")
    return str(json_file_path)


def convert_teachers_to_csv(teachers, output_dir="output"):
    """
    Convert teacher data to CSV with fields: name, description, url and date in filename

    Args:
        teachers (list): List of teacher dictionaries
        output_dir (str): Directory to save the CSV file

    Returns:
        str: Path to saved CSV file
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    date = get_current_date()
    csv_file_path = output_path / f"teachers-{date}.csv"

    # Prepare data for CSV
    csv_data = []

    for teacher in teachers:
        # Make sure teacher is a dictionary
        if not isinstance(teacher, dict):
            print(f"Warning: Skipping non-dict teacher: {teacher}")
            continue

        name = teacher.get("name", "")
        name_en = teacher.get("name_en", "")
        full_name = merge_teacher_names(name, name_en)
        name = full_name
        username = teacher.get("username", "")

        # Build description from available information
        description_parts = []

        # Add title/position
        # position = teacher.get("position", "")
        # if position:
        # description_parts.append(position)

        # Add title from teacher_title if available
        teacher_title = teacher.get("teacher_title", {})
        if isinstance(teacher_title, dict):
            title_en = teacher_title.get("title_en", "")
            if title_en:
                description_parts.append(title_en)

        # Add education from info if available
        # info = teacher.get("info", {})
        # if isinstance(info, dict):
        #     en_info = info.get("en", {})
        #     if isinstance(en_info, dict):
        #         education = en_info.get("education", "")
        #         if education:
        #             # Clean up education text (remove bullet points and extra whitespace)
        #             education_clean = education.replace("●", "").replace("•", "").strip()
        #             education_clean = " ".join(education_clean.split())
        #             if education_clean:
        #                 description_parts.append(education_clean)

        #         # Add academic interests if available
        #         academic = en_info.get("academic", "")
        #         if academic:
        #             academic_clean = academic.strip()
        #             if academic_clean:
        #                 description_parts.append(f"Research interests: {academic_clean}")

        # Combine description parts
        description = "; ".join(description_parts) if description_parts else ""

        # Build URL
        url = f"https://staff.bnbu.edu.cn/{username}/en" if username else ""

        csv_data.append({"name": name, "uid": username, "description": description, "url": url})

    # Save to CSV
    df = pd.DataFrame(csv_data)
    df.to_csv(csv_file_path, index=False, encoding="utf-8")

    print(f"✅ Saved teacher CSV to: {csv_file_path}")
    print(f"   Records: {len(csv_data)}")
    print(f"   Sample entries:")

    # Show first few entries
    for i, row in enumerate(csv_data[:3]):
        print(f"   {i+1}. {row['name']} -> {row['url']}")

    return str(csv_file_path)


def main():
    """
    Main function to fetch teachers, save as JSON, and convert to CSV
    """
    try:
        # Step 1: Fetch all teacher information
        teachers = fetch_all_teachers()

        if not teachers:
            print("❌ No teacher data fetched")
            return

        # Step 2: Save as JSON file
        json_path = save_teachers_json(teachers)

        # Step 3: Convert to CSV
        csv_path = convert_teachers_to_csv(teachers)

        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total teachers fetched: {len(teachers)}")
        print(f"JSON file: {json_path}")
        print(f"CSV file: {csv_path}")

    except requests.RequestException as e:
        print(f"❌ Error fetching data from API: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
