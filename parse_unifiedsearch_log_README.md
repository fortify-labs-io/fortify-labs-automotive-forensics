# Ford SYNC Unified Search Log GPS Analysis Tool

## Overview
This Python script analyzes Ford SYNC 3 unified search log files to extract and analyze GPS coordinates from reverse geocoding (rgc) entries. It identifies the most frequently visited locations by clustering GPS points within a 100-meter radius.

## Features
- ✅ Parses Ford SYNC unified search log files (System:QNX format)
- ✅ Extracts GPS coordinates from `rgc=&current_location=` entries
- ✅ Filters data by year (focuses on 2025 entries)
- ✅ Clusters locations within 100-meter radius using Haversine distance calculation
- ✅ Calculates centroid (center point) for each cluster
- ✅ Identifies top 3 most common locations
- ✅ Generates formatted analysis report with statistics
- ✅ Exports all GPS points with timestamps to separate log file
- ✅ Includes Google Maps links for each location

## Requirements
- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Usage

### Basic Usage
```bash
python parse_unifiedsearch_log.py <log_file_path>
```

### Example
```bash
python parse_unifiedsearch_log.py unifiedsearch.log
```

## Input Format
The script expects Ford SYNC unified search log files with entries in this format:

```
System:QNX
2025-01-15 08:23:45 | 62 | start initializing unified onebox engine
searchResourcePath=[/fs/sd/MAP/MAP_ANZ/index/], isSearchResourceAvailable=[true]
rgc=&current_location=-34.928500,138.600700&lang=en-GB&Priority=17
```

Key requirements:
- Each entry starts with "System:QNX"
- Timestamps in format: `YYYY-MM-DD HH:MM:SS`
- GPS coordinates in format: `rgc=&current_location=LAT,LON&lang=...`

## Output Files

### 1. GPS_Location_Analysis_Report_2025.txt
Formatted analysis report containing:
- Summary statistics (total points, unique clusters)
- Top 3 most common locations with:
  - Formatted coordinates (degrees N/S, E/W)
  - Cluster centroid coordinates
  - Point count and percentage
  - First and last visit timestamps
  - Google Maps link
- Combined statistics
- Additional details (date range, clustering precision)

### 2. AI-analysis_unifiedsearch-log.log
Complete list of all GPS points from 2025 with:
- Timestamp
- Original GPS coordinates (latitude, longitude)
- Simple pipe-delimited format for easy parsing

## How It Works

### 1. Log Parsing
- Reads the unified search log file line by line
- Identifies entry boundaries using "System:QNX" markers
- Extracts timestamps using regex pattern matching
- Extracts GPS coordinates from `rgc=` entries

### 2. Year Filtering
- Only processes entries with timestamps from 2025
- Ignores all other years to focus analysis

### 3. Location Clustering
- Uses Haversine formula to calculate great-circle distances between GPS points
- Groups points within 100 meters of each other into clusters
- Each point belongs to exactly one cluster
- Clustering algorithm:
  1. Takes first unassigned point as cluster seed
  2. Finds all nearby points within radius
  3. Marks them as assigned to this cluster
  4. Repeats until all points are assigned

### 4. Centroid Calculation
- Calculates the average (centroid) of all points in each cluster
- Provides a representative "center point" for the location
- More accurate than using any single GPS reading

### 5. Statistics & Ranking
- Sorts clusters by frequency (most common first)
- Calculates percentages and visit date ranges
- Identifies top 3 most frequently visited locations

## Example Output

```
================================================================================
GPS LOCATION ANALYSIS REPORT - 2025
================================================================================
Generated: 2025-01-21 05:17:05

SUMMARY
--------------------------------------------------------------------------------
Total GPS Points: 10
Unique Locations (clustered): 3

TOP 3 MOST COMMON LOCATIONS
--------------------------------------------------------------------------------

LOCATION #1
  Coordinates: 34.928520°S, 138.600720°E
  Clustered around: [-34.928520, 138.600720]
  Total Points: 5 (50.0% of all points)
  First Visit: 2025-01-15 08:23:45
  Last Visit: 2025-01-18 17:15:42
  Google Maps: https://www.google.com/maps?q=-34.928520,138.600720

LOCATION #2
  Coordinates: 33.815200°S, 151.003517°E
  Clustered around: [-33.815200, 151.003517]
  Total Points: 3 (30.0% of all points)
  First Visit: 2025-01-16 14:22:10
  Last Visit: 2025-01-16 15:10:22
  Google Maps: https://www.google.com/maps?q=-33.815200,151.003517

LOCATION #3
  Coordinates: 35.280850°S, 149.130250°E
  Clustered around: [-35.280850, 149.130250]
  Total Points: 2 (20.0% of all points)
  First Visit: 2025-01-17 10:05:44
  Last Visit: 2025-01-17 10:30:11
  Google Maps: https://www.google.com/maps?q=-35.280850,149.130250

COMBINED STATISTICS
--------------------------------------------------------------------------------
Top 3 locations combined: 10 points (100.0%)
Other locations: 0 points (0.0%)

ADDITIONAL DETAILS
--------------------------------------------------------------------------------
Date range: 2025-01-15 08:23:45 to 2025-01-18 17:15:42
Clustering precision: ~100 meters

================================================================================
```

## Technical Details

### Haversine Distance Formula
The script uses the Haversine formula to calculate distances between GPS coordinates:
- Accounts for the Earth's curvature
- Returns distance in meters
- Accurate for small distances (~100m clusters)
- Earth radius: 6,371,000 meters

### Clustering Precision
- Default radius: 100 meters
- Can be modified in the code if needed
- Balances between grouping nearby locations and distinguishing separate locations
- Suitable for analyzing parking locations, home/work locations, etc.

### Coordinate Formatting
- Input: Decimal degrees (e.g., -34.928500, 138.600700)
- Output: Degrees with direction (e.g., 34.928500°S, 138.600700°E)
- Precision: 6 decimal places (~0.11 meters at equator)

## Privacy Considerations
For your "Behind the Dashboard" blog series, remember to:
- ✅ Redact actual GPS coordinates in screenshots
- ✅ Use generic location names instead of exact addresses
- ✅ Consider blurring or removing Google Maps links if publishing
- ✅ The script output shows raw coordinates - sanitize before publishing

## Files Included
1. `parse_unifiedsearch_log.py` - Main analysis script
2. `test_unifiedsearch.log` - Sample log file for testing
3. `GPS_Location_Analysis_Report_2025.txt` - Example report output
4. `AI-analysis_unifiedsearch-log.log` - Example points log output
5. `README.md` - This file

## Use Cases
- Automotive forensics analysis
- Privacy research (understanding what data vehicles collect)
- Travel pattern analysis
- Identifying frequently visited locations
- Vehicle usage research
- Blog content for "Behind the Dashboard" series

## Troubleshooting

### No GPS data found
- Check that the log file contains `rgc=` entries
- Verify entries have the correct year (2025)
- Ensure timestamps are properly formatted

### Incorrect clustering
- Adjust the `radius_meters` parameter in `cluster_locations()` function
- Default is 100 meters
- Increase for broader clustering, decrease for finer granularity

### File encoding issues
- Script uses UTF-8 with error='ignore' for robustness
- Should handle most log file encoding issues automatically

## Author
Created for automotive cybersecurity research and forensic analysis at Fortify Labs.

## License
This tool is provided for legitimate automotive security research and forensic analysis purposes.
