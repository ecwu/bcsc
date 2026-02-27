#!/usr/bin/env python3
"""
Merge teacher data from latest API fetch with existing live data.

This script merges teacher data from the latest API fetch with the existing
live system data, handling resigned teachers and maintaining records for
teachers without UIDs.
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def get_current_date() -> str:
    """Return current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def load_csv_data(filepath: Path) -> List[Dict[str, str]]:
    """
    Load CSV data from file.

    Args:
        filepath: Path to CSV file

    Returns:
        List of dictionaries representing CSV rows
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)


def merge_teacher_data(
    latest_data: List[Dict[str, str]], live_data: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Merge latest API data with live data.

    Logic:
    1. If uid matches, override name, description, url, set incumbencyStatus to ACTIVE
    2. If uid exists in live data but not in latest, set incumbencyStatus to RESIGNED
    3. For rows without uid, keep as-is and move to end

    Args:
        latest_data: List of teachers from latest API fetch
        live_data: List of teachers from live system

    Returns:
        Merged list of teachers
    """
    # Build index of latest data by uid
    latest_by_uid: Dict[str, Dict[str, str]] = {}
    for row in latest_data:
        uid = row.get("uid", "").strip()
        if uid:
            latest_by_uid[uid] = row

    # Process live data
    merged_with_uid = []
    merged_without_uid = []
    resigned_count = 0
    updated_count = 0
    unchanged_count = 0
    new_count = 0

    # Track which latest UIDs have already been processed via live data
    seen_uids: set = set()

    for row in live_data:
        uid = row.get("uid", "").strip()

        if not uid:
            # No uid - keep as-is and move to end
            merged_without_uid.append(row)
            continue

        seen_uids.add(uid)

        if uid in latest_by_uid:
            # UID matches - override with latest data
            latest_row = latest_by_uid[uid]
            merged_row = row.copy()
            merged_row["name"] = latest_row.get("name", "")
            merged_row["description"] = latest_row.get("description", "")
            merged_row["url"] = latest_row.get("url", "")
            merged_row["incumbencyStatus"] = "ACTIVE"
            merged_with_uid.append(merged_row)
            updated_count += 1
        else:
            # UID not in latest - teacher resigned
            merged_row = row.copy()
            merged_row["incumbencyStatus"] = "RESIGNED"
            merged_with_uid.append(merged_row)
            resigned_count += 1

    # Add new teachers from latest data not present in live data
    for uid, row in latest_by_uid.items():
        if uid not in seen_uids:
            new_row = row.copy()
            new_row["incumbencyStatus"] = "ACTIVE"
            merged_with_uid.append(new_row)
            new_count += 1

    # Count unchanged (no-uid rows)
    unchanged_count = len(merged_without_uid)

    # Combine: rows with uid first, then rows without uid
    result = merged_with_uid + merged_without_uid

    print(f"Merge summary:")
    print(f"  Updated (ACTIVE): {updated_count}")
    print(f"  New teachers added: {new_count}")
    print(f"  Marked RESIGNED: {resigned_count}")
    print(f"  Unchanged (no uid): {unchanged_count}")
    print(f"  Total: {len(result)}")

    return result


def write_csv_data(data: List[Dict[str, str]], output_path: Path) -> None:
    """
    Write merged data to CSV file.

    Args:
        data: List of dictionaries representing rows
        output_path: Path to output CSV file
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not data:
            print("Warning: No data to write")
            return

        fieldnames = ["name", "uid", "description", "url", "incumbencyStatus"]

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Output file: {output_path}")
    except Exception as e:
        print(f"Error writing CSV: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Merge latest API teacher data with live system data"
    )
    parser.add_argument(
        "--latest_csv",
        required=True,
        help="Path to latest CSV from API fetch (teachers-{date}.csv)",
    )
    parser.add_argument(
        "--live_date",
        required=True,
        help="Date string for live data file (format: YYYY-MM-DD)",
    )

    args = parser.parse_args()

    # Paths
    latest_csv_path = Path(args.latest_csv)
    live_csv_path = (
        Path(__file__).parent / "live-data" / f"lecturers_export_{args.live_date}.csv"
    )

    # If file doesn't exist, try to find matching files (handles versioned files)
    if not live_csv_path.exists():
        live_data_dir = Path(__file__).parent / "live-data"
        matching_files = list(
            live_data_dir.glob(f"lecturers_export_{args.live_date}*.csv")
        )
        if matching_files:
            # Sort by modification time and pick the most recent
            matching_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            live_csv_path = matching_files[0]
            print(f"Found matching live data file: {live_csv_path.name}")
        else:
            print(f"Error: No live data file found matching '{args.live_date}'")
            sys.exit(1)

    # Validate that live_date contains a valid date
    date_part = args.live_date.split("-")[0:3]
    if len(date_part) != 3:
        print("Error: live_date must contain a valid date (YYYY-MM-DD[-N])")
        sys.exit(1)

    try:
        datetime.strptime("-".join(date_part), "%Y-%m-%d")
    except ValueError:
        print("Error: live_date must contain a valid date (YYYY-MM-DD[-N])")
        sys.exit(1)

    print(f"Merging teacher data...")
    print(f"Latest API data: {latest_csv_path}")
    print(f"Live system data: {live_csv_path}")

    # Load data
    latest_data = load_csv_data(latest_csv_path)
    live_data = load_csv_data(live_csv_path)

    print(f"Loaded {len(latest_data)} teachers from latest API data")
    print(f"Loaded {len(live_data)} teachers from live system data")

    # Merge data
    merged_data = merge_teacher_data(latest_data, live_data)

    # Write output with date versioning
    output_date = get_current_date()
    output_path = (
        Path(__file__).parent / "output" / f"lecturers_export_{output_date}.csv"
    )
    write_csv_data(merged_data, output_path)


if __name__ == "__main__":
    main()
