# GPS Location Analysis for Ford SYNC Unified Search Logs

Extracts and analyzes GPS coordinates from Ford SYNC `unifiedsearch.log` files to identify frequently visited locations.

## What It Does

* Parses `unifiedsearch.log` files for reverse geocoding GPS coordinates
* Filters data to 2025 entries only
* Clusters nearby locations (100m radius) to identify unique places
* Ranks locations by frequency of visits
* Generates analysis reports with Google Maps links

## Usage
```bash
python3 parse_unifiedsearch_log.py <log_file_path>
```

Example:
```bash
python3 parse_unifiedsearch_log.py unifiedsearch.log
```

The script will:
1. Extract all GPS coordinates from reverse geocoding entries
2. Filter to 2025 data only
3. Cluster nearby points into unique locations
4. Generate detailed analysis report

## Output

The script generates two files:

1. **GPS_Location_Analysis_Report_2025.txt** - Formatted analysis including:
   * Top 3 most visited locations
   * Coordinates and Google Maps links
   * Visit counts and percentages
   * First/last visit timestamps
   * Combined statistics

2. **AI-analysis_unifiedsearch-log.log** - Complete list of all GPS points with timestamps

## Viewing Locations

Open the Google Maps URLs from the report to view each location in your browser.

## Requirements

* Python 3.x (standard library only)
* `unifiedsearch.log` files from Ford SYNC 3 systems

## Configuration

Edit these values in the script to adjust behavior:
* `radius_meters=100` in `cluster_locations()` - Clustering precision
* Year filter in `parse_log_file()` - Currently set to 2025

## Author

Created for automotive cybersecurity research and forensic analysis at Fortify Labs.

## License

This tool is provided for legitimate automotive security research and forensic analysis purposes.
