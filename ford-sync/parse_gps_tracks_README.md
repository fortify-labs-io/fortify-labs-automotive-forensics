# GPS Track Parser for PAS Debug Logs

Extracts GPS tracks from Ford SYNC `pas_debug.log` files and creates time-enabled KML files for Google Earth visualization.

## What It Does

- Parses `pas_debug.log*` files for GPS coordinates
- Extracts map-matched coordinates (snapped to roads)
- Groups coordinates into trips based on time gaps
- Creates KML files with time-based playback for Google Earth

## Usage

```bash
python3 parse_gps_tracks.py
```

The script will:
1. Search the current directory for `pas_debug.log*` files
2. Extract and validate GPS coordinates
3. Group points into trips (2+ minute gaps = new trip)
4. Save KML files to `gps-tracks_pas-debug/` folder

## Output

Each trip generates a KML file named: `output_YYYY-MM-DD-HHMMSS.kml`

The KML includes:
- Start/end markers (green/red)
- Complete GPS track with timestamps
- Trip statistics (distance, duration, avg speed)

## Viewing in Google Earth

1. Open the KML file in Google Earth
2. Use the time slider at the top to play back the route
3. Adjust playback speed with slider controls

## Requirements

- Python 3.x (standard library only)
- `pas_debug.log` files from Ford SYNC 3 systems

## Filtering

The script automatically filters:
- Invalid GPS fixes (0.0, 0.0 coordinates)
- Coordinates outside valid ranges
- Trips with fewer than 3 points

## Configuration

Edit these values in `main()` to adjust behavior:
- `time_gap_minutes = 2` - Minutes between trips
- `min_points_per_trip = 3` - Minimum points per trip

## Author
Created for automotive cybersecurity research and forensic analysis at Fortify Labs.

## License
This tool is provided for legitimate automotive security research and forensic analysis purposes.
