# WiFi Location Matcher for Ford SYNC Logs

Finds WiFi networks detected near a specific GPS location by analyzing Ford SYNC `pas_debug.log` files.

## What It Does

* Searches `pas_debug.log*` files for WiFi network detections
* Matches WiFi detections to GPS coordinates within specified radius
* Identifies networks seen at target location
* Generates detailed report with network information

## Usage

```bash
python3 match_wifi_to_GPS_location.py -g "[lat, lon]" -o output.txt
```

Example:
```bash
python3 match_wifi_to_GPS_location.py -g "[-33.8568, 151.2153]" -o wifi_results.txt
```

With custom search radius:
```bash
python3 match_wifi_to_GPS_location.py -g "[-33.8568, 151.2153]" -o results.txt -d 100
```

## Command Line Options

* `-g` or `--gps` - GPS coordinates in format `[lat, lon]` (required)
* `-o` or `--output` - Output file path (required)
* `-d` or `--distance` - Search radius in meters (default: 50m)

## How It Works

1. Searches current directory for `pas_debug.log*` files
2. Extracts WiFi BSSID entries with timestamps
3. Finds corresponding GPS coordinates within ±2 seconds
4. Calculates distance from target location
5. Reports all WiFi networks within specified radius

## Output Report Includes

* **Individual Detections**: Each WiFi network seen at location with:
  - BSSID (MAC address) and SSID (network name)
  - Signal strength
  - GPS coordinates and distance from target
  - Timestamp information
  
* **SSID Summary**: Networks grouped by name showing:
  - Total detection count
  - Unique access points (BSSIDs)
  - Signal strength range
  
* **Network Summary**: Unique BSSID+SSID combinations with statistics

## Requirements

* Python 3.x (standard library only)
* `pas_debug.log*` files from Ford SYNC 3 systems

## Notes

* Script matches GPS data within 2-second window of WiFi detection
* Default search radius is 50 meters (adjustable)
* Processes multiple log files automatically (`.log`, `.log.1`, etc.)
* Hidden networks appear as "(Hidden Network)" in results

## Privacy Considerations

Output files contain:
* Exact GPS coordinates
* WiFi network names and MAC addresses
* Location timestamps

Store output files securely and follow appropriate data handling practices for forensic evidence.

## Author

Created for automotive cybersecurity research and forensic analysis.

## License

This tool is provided for legitimate automotive security research and forensic analysis purposes.
