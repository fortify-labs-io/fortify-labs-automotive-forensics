#!/usr/bin/env python3
"""
Extract GPS coordinates from pas_debug.log files
Processes NAV_FRAMEWORK_IF/SendGPSCanData logs and extracts MM (Map Matched) GPS positions
"""

import re
import glob
import os
from pathlib import Path

def find_pas_debug_files(directory='.'):
    """
    Find all files matching pas_debug.log* pattern
    
    Args:
        directory: Directory to search (default: current directory)
    
    Returns:
        List of matching file paths
    """
    pattern = os.path.join(directory, 'pas_debug.log*')
    files = sorted(glob.glob(pattern))
    return files

def extract_gps_data(line):
    """
    Extract timestamp and MM GPS position from log line
    
    Expected format:
    DD/MM/YYYY HH:MM:SS.mmm/ttt/ppp/NAV_FRAMEWORK_IF/SendGPSCanData/nnnn/=[...], [...], [MM Output: <SD2>Lon:xxx Lat:yyy Alt:zzz Hd:hhh</SD2>]
    
    Args:
        line: Log line to parse
    
    Returns:
        Tuple of (timestamp, longitude, latitude, altitude, heading) or None if no match
    """
    # Pattern to match the entire log line structure
    pattern = r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\.\d{3})/\d+/\d+/NAV_FRAMEWORK_IF/SendGPSCanData/.*?\[MM Output:\s*<SD2>Lon:([-\d.]+)\s+Lat:([-\d.]+)\s+Alt:([-\d.]+)\s+Hd:([-\d.]+)</SD2>\]'
    
    match = re.search(pattern, line)
    if match:
        timestamp = match.group(1)
        longitude = match.group(2)
        latitude = match.group(3)
        altitude = match.group(4)
        heading = match.group(5)
        return (timestamp, longitude, latitude, altitude, heading)
    
    return None

def process_files(files, output_file='extracted_detailed_GPS_pas-debug.log'):
    """
    Process all pas_debug.log files and extract GPS data
    
    Args:
        files: List of file paths to process
        output_file: Output file name for extracted data
    
    Returns:
        Number of GPS records extracted
    """
    gps_records = []
    
    print(f"Processing {len(files)} files...")
    
    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"  Reading: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if 'NAV_FRAMEWORK_IF/SendGPSCanData' in line and 'MM Output' in line:
                        gps_data = extract_gps_data(line)
                        if gps_data:
                            gps_records.append(gps_data)
        except Exception as e:
            print(f"    Error reading {filename}: {e}")
            continue
    
    # Write extracted data to output file
    print(f"\nWriting {len(gps_records)} GPS records to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# Extracted GPS Data from pas_debug.log files\n")
        f.write("# Format: Timestamp | Longitude | Latitude | Altitude | Heading\n")
        f.write("#" + "="*80 + "\n\n")
        
        for timestamp, lon, lat, alt, heading in gps_records:
            f.write(f"{timestamp} | Lon:{lon} | Lat:{lat} | Alt:{alt} | Hd:{heading}\n")
    
    return len(gps_records)

def main():
    """Main execution function"""
    print("="*80)
    print("GPS Data Extractor for pas_debug.log files")
    print("="*80)
    print()
    
    # Find all pas_debug.log* files
    files = find_pas_debug_files()
    
    if not files:
        print("ERROR: No files matching 'pas_debug.log*' found in current directory")
        return 1
    
    print(f"Found {len(files)} file(s) matching 'pas_debug.log*'")
    
    # Validate we have exactly 26 files
    if len(files) != 26:
        print(f"\nWARNING: Expected 26 files but found {len(files)}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
    else:
        print("✓ All 26 expected files found")
    
    print()
    
    # Process files and extract GPS data
    num_records = process_files(files)
    
    print()
    print("="*80)
    print(f"Extraction complete!")
    print(f"  Files processed: {len(files)}")
    print(f"  GPS records extracted: {num_records}")
    print(f"  Output file: extracted_detailed_GPS_pas-debug.log")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    exit(main())