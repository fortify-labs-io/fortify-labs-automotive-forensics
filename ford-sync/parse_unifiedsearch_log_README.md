# Ford SYNC PAS Debug Log GPS Track Parser

## Overview
This Python script extracts GPS tracks from Ford SYNC 3 `pas_debug.log` files and creates time-enabled KML files for Google Earth visualization. It parses map-matched GPS coordinates (snapped to roads) from the SendGPSCanData entries and groups them into individual trips for forensic analysis.

## Features
- ✅ Parses Ford SYNC `pas_debug.log*` files for GPS coordinates
- ✅ Extracts MM Output (Map Matched coordinates - snapped to roads)
- ✅ Filters invalid GPS fixes (0.0,0.0 and out-of-range coordinates)
- ✅ Groups coordinates into trips based on time gaps
- ✅ Calculates trip statistics (distance, duration, average speed)
- ✅ Creates time-enabled KML files for Google Earth playback
- ✅ Supports multiple log file formats (natural sorting)
- ✅ Includes start/end markers with trip metadata
- ✅ Uses Haversine formula for accurate distance calculations

## Requirements
- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Usage

### Basic Usage
```bash
python3 parse_gps_tracks.py
```

### What It Does
The script will automatically:
1. Search the current directory for `pas_debug.log*` files
2. Parse GPS coordinates from SendGPSCanData entries
3. Extract and validate map-matched coordinates
4. Filter out invalid GPS fixes
5. Group points into trips (2+ minute gaps = new trip)
6. Calculate trip statistics (distance, duration, speed)
7. Create time-enabled KML files in `gps-tracks_pas-debug/` folder

## Input Format
The script expects Ford SYNC PAS debug log files with entries containing:

```
11/15/2025 14:23:45.123 SendGPSCanData ... MM Output: Lon:xxxxxxxxxx Lat:-xxxxxxxxx Alt:45.5 Hd:180.0 ... SatInView:12
```

Key requirements:
- Timestamps in format: `MM/DD/YYYY HH:MM:SS.mmm`
- MM Output (Map Matched) coordinates in raw integer format
- Longitude and Latitude fields with adaptive precision decoding
- Altitude in meters, Heading in degrees
- SatInView (satellites in view) count

## Output Files

### KML Files (in gps-tracks_pas-debug/ folder)
Each trip generates a file named: `output_YYYY-MM-DD-HHMMSS.kml`

The KML file includes:
- **Start marker** (green) - Trip starting point
- **End marker** (red) - Trip ending point
- **Time-enabled GPS track** - Complete route with timestamps
- **Trip metadata** - Distance, duration, avg speed, point count
- **Playback controls** - Compatible with Google Earth time slider

## How It Works

### 1. Log File Discovery
- Searches for files matching: `pas_debug.log*`, `*pas_debug.log*`, `*pas_debug_log*`
- Sorts files naturally (handles numbered suffixes correctly)
- Reports file sizes and processes in order

### 2. GPS Coordinate Extraction
- Identifies lines containing `SendGPSCanData`
- Extracts timestamp using regex pattern matching
- Parses MM Output (Map Matched coordinates)
- Decodes raw coordinate values with adaptive precision:
  - Values > 1,000,000: divide by 100,000
  - Values < 1,000,000: divide by 10,000

### 3. Coordinate Validation
The script filters out invalid GPS data:
- Raw coordinates of 0.0, 0.0 (no GPS fix)
- Decoded coordinates near 0.0, 0.0 (South Atlantic "null island")
- Latitude outside range: -90° to 90°
- Longitude outside range: -180° to 180°

### 4. Trip Grouping
- Sorts all GPS points chronologically
- Groups points into trips based on time gaps
- Default threshold: 2+ minutes = new trip
- Maintains point order within each trip

### 5. Distance Calculation
Uses Haversine formula to calculate great-circle distances:
- Accounts for Earth's curvature
- Returns distance in meters
- Accurate for all trip lengths
- Earth radius: 6,371,000 meters

### 6. KML Generation
Creates Google Earth-compatible files with:
- `gx:Track` element for time-based playback
- ISO 8601 timestamps for each point
- Color-coded track (red line, customizable width)
- Start/end placemarks with descriptions
- Trip statistics in document metadata

## Viewing in Google Earth

### Desktop Application
1. Open the KML file in Google Earth Pro or Google Earth
2. Find the **time slider** at the top of the screen
3. Click the **play button** to animate the route
4. Adjust playback speed with the slider controls
5. Use the **date/time range selectors** for specific segments

### Web Version
1. Go to [earth.google.com](https://earth.google.com)
2. Click **Projects** → **Import KML file from computer**
3. Upload the KML file
4. The route will display with time information

## Configuration

Edit these values in the `main()` function to adjust behavior:

```python
# Time gap between trips (minutes)
time_gap_minutes = 2  # Default: 2 minutes

# Minimum points required to save a trip
min_points_per_trip = 3  # Default: 3 points

# Search patterns for log files
search_patterns = ['pas_debug.log*', '*pas_debug.log*', '*pas_debug_log*']

# Output folder name
output_folder = 'gps-tracks_pas-debug'
```

### Natural Sorting
Uses natural sort algorithm for log files:
- `pas_debug.log` → `pas_debug.log.1` → `pas_debug.log.2`
- Not: `pas_debug.log` → `pas_debug.log.2` → `pas_debug.log.1`
- Handles numeric suffixes correctly

## Use Cases
- Automotive forensics analysis
- Accident reconstruction (trip replay)
- Travel pattern analysis
- Vehicle usage investigation
- Privacy research (understanding GPS data collection)
- Blog content for "Behind the Dashboard" series
- Expert witness testimony preparation

## Privacy Considerations

- ✅ Redact actual GPS coordinates in screenshots
- ✅ Use generic location names instead of exact addresses
- ✅ Blur KML visualization maps if publishing
- ✅ Consider offset coordinates for demonstration purposes
- ✅ The script output shows real coordinates - sanitize before publishing

## Files Generated
1. `gps-tracks_pas-debug/` - Output folder (created automatically)
2. `output_YYYY-MM-DD-HHMMSS.kml` - One file per trip
3. Console output with statistics and validation info

## Author
Created for automotive cybersecurity research and forensic analysis at Fortify Labs.

## License
This tool is provided for legitimate automotive security research and forensic analysis purposes.
