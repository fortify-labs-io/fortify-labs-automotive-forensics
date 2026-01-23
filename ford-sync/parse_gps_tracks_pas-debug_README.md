# GPS Track Parser for PAS Debug Logs

Python script for parsing GPS tracks directly from Ford SYNC 3 `pas_debug.log` files, extracting Map Matched (MM) GPS coordinates, and exporting time-enabled KML files for visualization in Google Earth.

## Features

- **Direct Log Processing**: Reads raw `pas_debug.log*` files directly (no extraction step required)
- **Map Matched Coordinates**: Extracts MM Output (coordinates snapped to roads) for accurate visualization
- **Automatic Trip Separation**: Splits GPS tracks based on time gaps (default: 2 minutes)
- **Coordinate Validation**: Filters out invalid GPS fixes (0,0 coordinates, out-of-range values)
- **Time-Enabled KML**: Generates interactive KML files with:
  - Time-based playback in Google Earth
  - Distance and speed calculations
  - Start/End markers
  - Trip duration and statistics
- **Natural File Sorting**: Correctly processes multiple log files in chronological order
- **Comprehensive Statistics**: Provides detailed summary of trips, distances, and filtering results

## Requirements

- Python 3.6 or higher
- No external dependencies (uses standard library only)

## Usage

### Basic Usage

Process pas_debug.log files in the current directory:

```bash
python3 parse_gps_tracks_pas-debug.py
```

The script will automatically find all files matching:
- `pas_debug.log*`
- `*pas_debug.log*`
- `*pas_debug_log*`

### Configuration

Edit these variables at the top of `main()` to customize behavior:

```python
time_gap_minutes = 2        # Time gap to separate trips
min_points_per_trip = 3     # Minimum points to save a trip
output_folder = 'gps-tracks_pas-debug'  # Output directory
```

## Input File Format

The script parses raw pas_debug.log lines with this structure:

```
DD/MM/YYYY HH:MM:SS.mmm/thread/priority/NAV_FRAMEWORK_IF/SendGPSCanData/line/=[DR Output: <SD2>...</SD2>], [signal_type:X SatInView:YY], [MM Output: <SD2>Lon:XXX Lat:YYY Alt:ZZZ Hd:HHH</SD2>]
```

### Extracted Data

From each `MM Output` section, the script extracts:
- **Timestamp**: Date and time of GPS position
- **Longitude**: Map-matched longitude
- **Latitude**: Map-matched latitude
- **Altitude**: Altitude in meters
- **Heading**: Vehicle heading in degrees
- **Satellites**: Number of satellites in view

## Coordinate Decoding

The script uses **adaptive coordinate decoding** based on empirical testing with Ford SYNC data:

```python
def decode_mm_coordinate(mm_value):
    if abs(mm_value) > 1000000:
        return mm_value / 100000  # Large values: ÷100,000
    else:
        return mm_value / 10000   # Small values: ÷10,000
```

**Example Conversion:**
```
Input:  Lon:15129673.819989
Output: 151.29673819989° E (Sydney, Australia)
```

## Coordinate Validation

The script filters out invalid GPS positions:

### Invalid Coordinates Filtered

1. **(0, 0) Raw Coordinates**: Pre-decoding filter for null GPS data
2. **Out-of-Range Values**: Post-decoding validation
   - Latitude must be between -90° and 90°
   - Longitude must be between -180° and 180°
3. **Near-Zero Coordinates**: Filters `|lat| < 0.001 AND |lon| < 0.001` to catch bad fixes

### Why Validation Matters

Ford SYNC systems output GPS data even when:
- GPS signal is lost (tunnels, parking garages)
- System is initializing or cold-starting
- Vehicle is in areas with poor satellite visibility
- Sensors are providing Dead Reckoning estimates

Only valid Map Matched positions are exported for accurate route visualization.

## Output

### Directory Structure

```
gps-tracks_pas-debug/
├── output_2025-07-27-151953.kml
├── output_2025-07-28-082756.kml
├── output_2025-07-28-095853.kml
└── ...
```

### KML Filenames

Files are named using the trip start timestamp: `output_YYYY-MM-DD-HHMMSS.kml`

### KML Features

Each time-enabled KML file includes:
- **Track**: Time-stamped GPS path for playback
- **Start Marker**: Green circle at trip beginning
- **End Marker**: Red circle at trip end
- **Trip Metadata**: Duration, distance, average speed, point count
- **Interactive Playback**: Use Google Earth's time slider

## Trip Separation Logic

Trips are automatically separated based on **time gaps only**:

- **New Trip Threshold**: 2+ minute gap between consecutive GPS points
- **Minimum Trip Size**: 3+ points required to save a trip

Typical gap causes:
- Vehicle was turned off
- GPS signal was lost
- Extended stationary period (e.g., parked)
- Log file rotation

## Processing Summary

### Console Output

```
Searching for GPS data in: /path/to/logs
Patterns: pas_debug.log*, *pas_debug.log*, *pas_debug_log*
Time gap for new trip: 2 minutes
======================================================================

Found 26 log file(s):
  - pas_debug.log (12.34 MB)
  - pas_debug.log.1 (15.67 MB)
  ...

Parsing GPS data...
  Processing pas_debug.log... 1523 valid GPS points (87 filtered)
  Processing pas_debug.log.1... 2341 valid GPS points (142 filtered)
  ...

Total GPS points: 44709
Bad coordinates filtered: 623 (including 0.0,0.0 invalid fixes)

Grouping into trips (gap: 2 min)...
Found 66 trip(s)

Creating time-enabled KML files:
----------------------------------------------------------------------
✓ output_2025-07-27-151953.kml
    2025-07-27 15:19:53 → 17:41:16
    141.3 min, 85.42 km, 8351 points

✓ output_2025-07-28-082756.kml
    2025-07-28 08:27:56 → 08:40:48
    12.9 min, 8.73 km, 765 points

...

======================================================================
SUCCESS! Created 66 time-enabled KML file(s)
Location: gps-tracks_pas-debug/

To view in Google Earth:
  1. Open the KML file
  2. Use the time slider at the top to play back the route
  3. Adjust playback speed with the slider controls
```

## Trip Statistics

Each trip includes calculated metrics:

- **Duration**: Total time from first to last GPS point
- **Distance**: Haversine distance calculation (accounts for Earth's curvature)
- **Average Speed**: Distance ÷ Duration (km/h)
- **Point Count**: Number of GPS coordinates in the trip

**Example Trip Metadata in KML:**
```
Start: 2023-07-27 15:19:53
End: 2023-07-27 17:41:16
Duration: 141.3 minutes
Distance: 35.42 km
Avg Speed: 34.3 km/h
Points: 4531
```

## Google Earth Playback

Time-enabled KML files support interactive visualization:

1. **Open in Google Earth**: Double-click the KML file
2. **Time Slider**: Appears at top of Google Earth window
3. **Playback Controls**: 
   - Play/Pause button
   - Speed adjustment slider
   - Time range selector
4. **Camera Follow**: Enable "Follow" mode to track the vehicle automatically

## Natural File Sorting

The script uses natural sorting to process log files in correct order:

```python
def natural_sort_key(filename):
    parts = re.split(r'(\d+)', filename)
    return [int(part) if part.isdigit() else part.lower() for part in parts]
```

**Result:**
- ✅ Correct: `pas_debug.log`, `pas_debug.log.1`, `pas_debug.log.2`, ..., `pas_debug.log.25`
- ❌ Wrong: `pas_debug.log`, `pas_debug.log.1`, `pas_debug.log.10`, `pas_debug.log.2`

## Technical Notes

### Map Matched vs Dead Reckoning

- **MM (Map Matched)**: GPS coordinates snapped to known road networks
  - Most accurate for route visualization
  - Requires GPS satellite lock
  - This script extracts MM data only

- **DR (Dead Reckoning)**: Estimated position using vehicle sensors
  - Gyroscope, wheel speed, compass
  - Used when GPS signal is unavailable
  - Not extracted by this script

### Haversine Distance Calculation

The script calculates actual driving distance using the Haversine formula, which accounts for the Earth's spherical geometry:

```python
def calculate_trip_distance(trip):
    # Uses Earth's radius (6,371 km) and spherical trigonometry
    # Returns distance in meters
```

This provides accurate distance measurements for forensic analysis.

### Adaptive Coordinate Decoding

Based on empirical analysis of Ford SYNC data, the script uses different divisors:
- **Large coordinates** (>1,000,000): Divide by 100,000
- **Small coordinates** (<1,000,000): Divide by 10,000

This adaptive approach handles the variable precision in Ford's GPS coordinate encoding.

## Use Cases

- **Forensic Analysis**: Reconstructing vehicle movements with accurate timestamps
- **Route Visualization**: Examining travel patterns and locations visited
- **Temporal Analysis**: Analyzing when and where vehicles traveled
- **Speed Analysis**: Identifying speeding or unusual driving patterns

## Privacy & Security

**Warning**: GPS data reveals detailed location history and travel patterns. Handle extracted data appropriately:

- Redact or anonymize data before sharing publicly
- Consider the sensitivity of location data in forensic contexts

## Limitations

- **Requires Raw Logs**: Script needs original `pas_debug.log*` files from eMMC extraction
- **MM Data Only**: Does not extract Dead Reckoning positions

## License

This script is provided as-is for automotive forensics and security research purposes.

## Author

Created by Fortify Labs for automotive cybersecurity research and forensic analysis.

---

**For more information about Ford SYNC forensics and automotive cybersecurity research, visit the Fortify Labs blog.**