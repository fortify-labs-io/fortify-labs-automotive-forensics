

#!/usr/bin/env python3
"""
GPS Track Parser for PAS Debug Logs
Parses pas_debug.log* files, extracts GPS tracks from MM Output (Map Matched coordinates), 
and saves each trip as a time-enabled KML file.
MM Output provides map-matched coordinates (snapped to roads) for accurate visualization.
"""
import re
import os
import glob
import math
from datetime import datetime, timedelta
from pathlib import Path

def natural_sort_key(filename):
    """Generate a key for natural sorting of filenames with numbers"""
    parts = re.split(r'(\d+)', filename)
    return [int(part) if part.isdigit() else part.lower() for part in parts]

def parse_dms_to_decimal(degrees, minutes, seconds):
    """Convert degrees, minutes, seconds to decimal degrees"""
    decimal = abs(degrees) + minutes/60 + seconds/3600
    if degrees < 0:
        decimal = -decimal
    return decimal

def decode_mm_coordinate(mm_value):
    """
    Decode MM coordinate with adaptive precision.
    MM format uses different multipliers based on coordinate magnitude:
    - Large values (>1000000): divide by 100000
    - Smaller values (<1000000): divide by 10000
    """
    if abs(mm_value) > 1000000:
        return mm_value / 100000
    else:
        return mm_value / 10000

def parse_gps_line(line):
    """Parse a GPS log line and extract coordinates and timestamp - using MM Output (Map Matched)"""
    timestamp_match = re.match(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3})', line)
    if not timestamp_match:
        return None
    
    timestamp_str = timestamp_match.group(1)
    timestamp = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S.%f')
    
    # Extract MM Output (Map Matched coordinates - snapped to roads)
    mm_match = re.search(
        r'MM Output:.*?Lon:([\d.-]+)\s+Lat:([\d.-]+)\s+Alt:([\d.-]+)\s+Hd:([\d.-]+)',
        line
    )
    
    if not mm_match:
        return None
    
    mm_lon_raw = float(mm_match.group(1))
    mm_lat_raw = float(mm_match.group(2))
    
    # Filter out invalid/bad coordinates
    # Skip if coordinates are 0.0 (invalid GPS fix - usually means no signal)
    if mm_lon_raw == 0.0 and mm_lat_raw == 0.0:
        return None
    
    # Decode with adaptive precision
    longitude = decode_mm_coordinate(mm_lon_raw)
    latitude = decode_mm_coordinate(mm_lat_raw)
    altitude_m = float(mm_match.group(3))
    heading = float(mm_match.group(4))
    
    # Validate coordinates (lat: -90 to 90, lon: -180 to 180)
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    
    # Additional filter: reject coordinates at exactly 0.0, 0.0 after decoding
    # This catches bad GPS fixes that appear in the South Atlantic
    if abs(longitude) < 0.001 and abs(latitude) < 0.001:
        return None
    
    sat_match = re.search(r'SatInView:(\d+)', line)
    satellites = int(sat_match.group(1)) if sat_match else 0
    
    return {
        'timestamp': timestamp,
        'latitude': latitude,
        'longitude': longitude,
        'altitude_ft': altitude_m * 3.28084,  # Convert to feet for consistency
        'altitude_m': altitude_m,
        'heading': heading,
        'satellites': satellites
    }

def calculate_trip_distance(trip):
    """Calculate total distance traveled in a trip using Haversine formula (meters)"""
    if len(trip) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(1, len(trip)):
        lat1 = math.radians(trip[i-1]['latitude'])
        lon1 = math.radians(trip[i-1]['longitude'])
        lat2 = math.radians(trip[i]['latitude'])
        lon2 = math.radians(trip[i]['longitude'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_m = 6371000 * c
        
        total_distance += distance_m
    
    return total_distance

def group_into_trips(gps_points, time_gap_minutes=2):
    """Group GPS points into trips based on time gaps"""
    if not gps_points:
        return []
    
    gps_points.sort(key=lambda x: x['timestamp'])
    
    trips = []
    current_trip = [gps_points[0]]
    
    for point in gps_points[1:]:
        time_diff = (point['timestamp'] - current_trip[-1]['timestamp']).total_seconds() / 60
        
        if time_diff > time_gap_minutes:
            trips.append(current_trip)
            current_trip = [point]
        else:
            current_trip.append(point)
    
    if current_trip:
        trips.append(current_trip)
    
    return trips

def create_kml_file(trip, filename):
    """Create a time-enabled KML file for Google Earth playback"""
    
    if not trip:
        return
    
    start_time = trip[0]['timestamp']
    end_time = trip[-1]['timestamp']
    duration_min = (end_time - start_time).total_seconds() / 60
    distance_m = calculate_trip_distance(trip)
    distance_km = distance_m / 1000
    avg_speed_kmh = (distance_km / (duration_min / 60)) if duration_min > 0 else 0
    
    # KML with gx namespace for time-based tracks
    kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <name>GPS Track - {start_time.strftime('%Y-%m-%d %H:%M:%S')}</name>
    <description><![CDATA[
      <b>Start:</b> {start_time.strftime('%Y-%m-%d %H:%M:%S')}<br/>
      <b>End:</b> {end_time.strftime('%Y-%m-%d %H:%M:%S')}<br/>
      <b>Duration:</b> {duration_min:.1f} minutes<br/>
      <b>Distance:</b> {distance_km:.2f} km<br/>
      <b>Avg Speed:</b> {avg_speed_kmh:.1f} km/h<br/>
      <b>Points:</b> {len(trip)}
    ]]></description>
    
    <Style id="track-normal">
      <IconStyle>
        <scale>0.5</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>
        </Icon>
      </IconStyle>
      <LineStyle>
        <color>ff0000ff</color>
        <width>3</width>
      </LineStyle>
    </Style>
    
    <Style id="track-highlight">
      <IconStyle>
        <scale>0.7</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png</href>
        </Icon>
      </IconStyle>
      <LineStyle>
        <color>ff0000ff</color>
        <width>5</width>
      </LineStyle>
    </Style>
    
    <StyleMap id="track-style">
      <Pair>
        <key>normal</key>
        <styleUrl>#track-normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#track-highlight</styleUrl>
      </Pair>
    </StyleMap>
    
    <Style id="startIcon">
      <IconStyle>
        <color>ff00ff00</color>
        <scale>1.1</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
    
    <Style id="endIcon">
      <IconStyle>
        <color>ff0000ff</color>
        <scale>1.1</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
    
    <Placemark>
      <name>Start</name>
      <description>Trip started at {start_time.strftime('%H:%M:%S')}</description>
      <styleUrl>#startIcon</styleUrl>
      <Point>
        <coordinates>{trip[0]['longitude']},{trip[0]['latitude']},{trip[0]['altitude_m']}</coordinates>
      </Point>
    </Placemark>
    
    <Placemark>
      <name>End</name>
      <description>Trip ended at {end_time.strftime('%H:%M:%S')}</description>
      <styleUrl>#endIcon</styleUrl>
      <Point>
        <coordinates>{trip[-1]['longitude']},{trip[-1]['latitude']},{trip[-1]['altitude_m']}</coordinates>
      </Point>
    </Placemark>
    
    <Placemark>
      <name>GPS Track with Time</name>
      <description><![CDATA[
        Time-enabled track - use the time slider in Google Earth to play back the route.<br/>
        Distance: {distance_km:.2f} km<br/>
        Avg Speed: {avg_speed_kmh:.1f} km/h
      ]]></description>
      <styleUrl>#track-style</styleUrl>
      <gx:Track>
        <altitudeMode>absolute</altitudeMode>
'''
    
    # Add timestamps
    for point in trip:
        timestamp_iso = point['timestamp'].strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        kml += f'        <when>{timestamp_iso}</when>\n'
    
    # Add coordinates
    for point in trip:
        kml += f'        <gx:coord>{point["longitude"]} {point["latitude"]} {point["altitude_m"]}</gx:coord>\n'
    
    kml += '''      </gx:Track>
    </Placemark>
  </Document>
</kml>
'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(kml)

def main():
    """Main function"""
    
    # Configuration
    search_patterns = ['pas_debug.log*', '*pas_debug.log*', '*pas_debug_log*']
    output_folder = 'gps-tracks_pas-debug'
    time_gap_minutes = 2  # Only criterion: 2+ minute gap = new trip
    min_points_per_trip = 3  # Minimum points to save a trip
    
    current_dir = os.getcwd()
    print(f"Searching for GPS data in: {current_dir}")
    print(f"Patterns: {', '.join(search_patterns)}")
    print(f"Time gap for new trip: {time_gap_minutes} minutes")
    print("=" * 70)
    
    # Find log files
    log_files = []
    for pattern in search_patterns:
        log_files.extend(glob.glob(pattern))
    
    log_files = list(set(log_files))
    log_files.sort(key=natural_sort_key)
    log_files.reverse()
    
    if not log_files:
        print(f"ERROR: No files found matching patterns")
        return
    
    log_files.sort()
    print(f"Found {len(log_files)} log file(s):")
    for log_file in log_files:
        file_size = os.path.getsize(log_file) / (1024 * 1024)
        print(f"  - {log_file} ({file_size:.2f} MB)")
    print()
    
    # Parse GPS data
    print("Parsing GPS data...")
    all_gps_points = []
    total_lines_with_gps = 0
    
    for log_file in log_files:
        print(f"  Processing {log_file}...", end=' ')
        points_found = 0
        lines_with_gps = 0
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'SendGPSCanData' in line:
                        lines_with_gps += 1
                        gps_data = parse_gps_line(line)
                        if gps_data:
                            all_gps_points.append(gps_data)
                            points_found += 1
            filtered = lines_with_gps - points_found
            if filtered > 0:
                print(f"{points_found} valid GPS points ({filtered} filtered)")
            else:
                print(f"{points_found} GPS points")
            total_lines_with_gps += lines_with_gps
        except Exception as e:
            print(f"ERROR: {e}")
    
    total_filtered = total_lines_with_gps - len(all_gps_points)
    print(f"\nTotal GPS points: {len(all_gps_points)}")
    if total_filtered > 0:
        print(f"Bad coordinates filtered: {total_filtered} (including 0.0,0.0 invalid fixes)")
    
    if not all_gps_points:
        print("No GPS data found!")
        return
    
    # Group into trips
    print(f"\nGrouping into trips (gap: {time_gap_minutes} min)...")
    trips = group_into_trips(all_gps_points, time_gap_minutes=time_gap_minutes)
    print(f"Found {len(trips)} trip(s)")
    
    # Filter trips by minimum points only
    valid_trips = [trip for trip in trips if len(trip) >= min_points_per_trip]
    
    if len(valid_trips) < len(trips):
        print(f"Filtered to {len(valid_trips)} trip(s) with at least {min_points_per_trip} points")
    
    if not valid_trips:
        print("\nNo valid trips found!")
        return
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Save trips
    print(f"\nCreating time-enabled KML files:")
    print("-" * 70)
    
    for trip in valid_trips:
        start_time = trip[0]['timestamp']
        filename = f"output_{start_time.strftime('%Y-%m-%d-%H%M%S')}.kml"
        filepath = os.path.join(output_folder, filename)
        
        create_kml_file(trip, filepath)
        
        end_time = trip[-1]['timestamp']
        duration_min = (end_time - start_time).total_seconds() / 60
        distance_m = calculate_trip_distance(trip)
        
        print(f"✓ {filename}")
        print(f"    {start_time.strftime('%Y-%m-%d %H:%M:%S')} → {end_time.strftime('%H:%M:%S')}")
        print(f"    {duration_min:.1f} min, {distance_m/1000:.2f} km, {len(trip)} points")
        print()
    
    print("=" * 70)
    print(f"SUCCESS! Created {len(valid_trips)} time-enabled KML file(s)")
    print(f"Location: {output_folder}/")
    print()
    print("To view in Google Earth:")
    print("  1. Open the KML file")
    print("  2. Use the time slider at the top to play back the route")
    print("  3. Adjust playback speed with the slider controls")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
