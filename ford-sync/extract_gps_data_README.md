# Ford SYNC PAS Debug Log GPS Data Extractor

## Overview
This Python script extracts GPS coordinates from Ford SYNC 3 `pas_debug.log` files by parsing NAV_FRAMEWORK_IF/SendGPSCanData entries. It creates a consolidated log file containing all GPS positions with timestamps for further analysis or processing.

## Features
- ✅ Processes multiple `pas_debug.log*` files automatically
- ✅ Extracts MM Output (Map Matched) GPS coordinates from SendGPSCanData entries
- ✅ Captures timestamp, longitude, latitude, altitude, and heading
- ✅ Validates expected file count (26 files typical for full extraction)
- ✅ Consolidates all GPS data into single output file
- ✅ Pipe-delimited format for easy parsing
- ✅ UTF-8 encoding with error handling for robust processing

## Requirements
- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Usage

### Basic Usage
```bash
python3 extract_gps_data.py
```

### What It Does
The script will automatically:
1. Search current directory for all `pas_debug.log*` files
2. Validate file count (expects 26 files, warns if different)
3. Parse each file for NAV_FRAMEWORK_IF/SendGPSCanData entries
4. Extract MM Output GPS data (Map Matched coordinates)
5. Write all GPS records to `extracted_detailed_GPS_pas-debug.log`

### Interactive Validation
If file count differs from expected 26 files:
```
WARNING: Expected 26 files but found 15
Continue anyway? (y/n):
```

## Input Format
The script expects Ford SYNC PAS debug log files with entries in this format:

```
08/15/2025 14:23:45.123/12345/67890/NAV_FRAMEWORK_IF/SendGPSCanData/1234/=[...], [...], [MM Output: <SD2>Lon:1386007200 Lat:-349285200 Alt:45.5 Hd:180.0</SD2>]
```

Key requirements:
- Timestamp: `DD/MM/YYYY HH:MM:SS.mmm` format
- Component: `NAV_FRAMEWORK_IF/SendGPSCanData`
- MM Output section with XML-style tags: `<SD2>...</SD2>`
- GPS fields: Lon (longitude), Lat (latitude), Alt (altitude), Hd (heading)

## Output Files

### extracted_detailed_GPS_pas-debug.log
Consolidated GPS data file containing:

```
# Extracted GPS Data from pas_debug.log files
# Format: Timestamp | Longitude | Latitude | Altitude | Heading
#================================================================================

08/15/2025 14:23:45.123 | Lon:xxxxxxxxxx | Lat:-xxxxxxxxx | Alt:45.5 | Hd:180.0
```

**File format details:**
- Header with format description
- Pipe-delimited fields for easy parsing
- Raw coordinate values (not decoded)
- Altitude in meters
- Heading in degrees (0-360)
- Chronological order as found in source files

## How It Works

### 1. File Discovery
- Searches for files matching `pas_debug.log*` pattern
- Sorts files alphabetically/numerically
- Reports total file count
- Validates against expected count (26 files)

### 2. Pattern Matching
Uses regex to identify and extract GPS data:
```regex
(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\.\d{3})/\d+/\d+/NAV_FRAMEWORK_IF/SendGPSCanData/.*?\[MM Output:\s*<SD2>Lon:([-\d.]+)\s+Lat:([-\d.]+)\s+Alt:([-\d.]+)\s+Hd:([-\d.]+)</SD2>\]
```

### 3. Data Extraction
For each matching line:
1. Extracts timestamp (DD/MM/YYYY HH:MM:SS.mmm)
2. Captures longitude (raw integer value)
3. Captures latitude (raw integer value)
4. Captures altitude (meters, decimal)
5. Captures heading (degrees, decimal)

### 4. Output Generation
- Writes header with format information
- Outputs one GPS record per line
- Preserves chronological order from source files
- Uses pipe delimiters for easy parsing

## Technical Details

### Raw Coordinate Format
- **Longitude/Latitude**: Integer values requiring decoding
- **Example**: `xxxxxxxxxx` → `xxx.600720°E` (divide by 10,000,000)
- **Note**: This script outputs raw values; decode separately if needed

### Map Matched Coordinates
The MM Output provides:
- **Map Matched**: Coordinates snapped to road network
- **More accurate**: Than raw GPS for route visualization
- **Road-aware**: Eliminates GPS drift to non-road areas

### File Processing
- **Line-by-line**: Memory-efficient processing
- **UTF-8 encoding**: With error='ignore' for robustness
- **Error handling**: Continues on file read errors
- **Sorted order**: Natural file ordering maintained

### Expected File Count
Ford SYNC typically rotates 26 log files:
- `pas_debug.log` (current)
- `pas_debug.log.1` through `pas_debug.log.25` (rotated)

Different counts may indicate:
- Partial extraction from vehicle
- Recent system reset/reflash
- Different logging configuration

## Use Cases
- Pre-processing for GPS track analysis
- Automotive forensics data consolidation
- Coordinate extraction for mapping tools
- Input preparation for KML generation scripts
- Timeline analysis of vehicle movements
- Data export for external analysis tools
- Blog content preparation for "Behind the Dashboard" series

## Integration with Other Tools

### With parse_gps_tracks.py
This extractor creates a simplified format. For full trip analysis:
1. Use `parse_gps_tracks.py` directly on `pas_debug.log` files
2. That script includes decoding, trip grouping, and KML generation

### Custom Processing Pipeline
```bash
# Step 1: Extract GPS data
python3 extract_gps_data.py

# Step 2: Process with custom tools
python3 your_analysis_script.py extracted_detailed_GPS_pas-debug.log

# Step 3: Generate visualizations
python3 your_mapping_script.py
```

## Configuration

### Customize Output File
Edit the `process_files()` call in `main()`:
```python
num_records = process_files(files, output_file='custom_output.log')
```

### Disable File Count Validation
Comment out or modify the validation section:
```python
# Validate we have exactly 26 files
# if len(files) != 26:
#     print(f"\nWARNING: Expected 26 files but found {len(files)}")
#     ...
```

### Change Search Directory
Modify the `find_pas_debug_files()` call:
```python
files = find_pas_debug_files(directory='/path/to/logs')
```

## Privacy Considerations

- ✅ Raw coordinates require decoding to be human-readable
- ✅ Consider redacting specific coordinates in examples
- ✅ Use generic timestamps or offset dates
- ✅ The output file contains raw tracking data - sanitize before publishing
- ✅ Consider aggregating data to show patterns without exact locations

## Author
Created for automotive cybersecurity research and forensic analysis at Fortify Labs.

## License
This tool is provided for legitimate automotive security research and forensic analysis purposes.
