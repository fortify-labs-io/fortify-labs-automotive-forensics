#!/usr/bin/env python3
"""
Match WiFi networks to GPS locations from Ford SYNC pas_debug log files.

This script analyzes pas_debug.log.* files to find WiFi networks detected
within 50 meters of a specified GPS coordinate.
"""

import argparse
import glob
import re
import sys
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
from typing import List, Tuple, Dict, Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1, lon1: First point coordinates in decimal degrees
        lat2, lon2: Second point coordinates in decimal degrees
    
    Returns:
        Distance in meters
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of Earth in meters
    r = 6371000
    
    return c * r


def parse_timestamp(ts_str: str) -> datetime:
    """
    Parse timestamp from log format: MM/DD/YYYY HH:MM:SS.mmm
    
    Args:
        ts_str: Timestamp string from log
    
    Returns:
        datetime object
    """
    # Format: MM/DD/YYYY HH:MM:SS.mmm
    return datetime.strptime(ts_str, "%m/%d/%Y %H:%M:%S.%f")


def convert_mm_coordinates(mm_lon: float, mm_lat: float) -> Tuple[float, float]:
    """
    Convert Map Matched coordinates to decimal degrees.
    
    The MM Output format is decimal degrees scaled by 100000.
    For example: MM Lon: 13572514.899124 = 135.72514899124°
    
    Args:
        mm_lon: Map Matched longitude value
        mm_lat: Map Matched latitude value
    
    Returns:
        Tuple of (latitude, longitude) in decimal degrees
    """
    # Simply divide by 100000 to get decimal degrees
    longitude = mm_lon / 100000
    latitude = mm_lat / 100000
    
    return latitude, longitude


def extract_bssid_entries(log_content: List[str]) -> List[Dict]:
    """
    Extract BSSID entries with timestamps from log content.
    
    Args:
        log_content: List of log lines
    
    Returns:
        List of dicts containing timestamp, BSSID, and line number
    """
    bssid_pattern = re.compile(
        r'^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}).*Extracted BSSID = ([0-9a-fA-F:]+)'
    )
    
    entries = []
    for idx, line in enumerate(log_content):
        match = bssid_pattern.match(line)
        if match:
            timestamp_str = match.group(1)
            bssid = match.group(2)
            entries.append({
                'timestamp': parse_timestamp(timestamp_str),
                'timestamp_str': timestamp_str,
                'bssid': bssid,
                'line_num': idx
            })
    
    return entries


def extract_ssid_and_signal(log_content: List[str], line_num: int) -> Tuple[Optional[str], Optional[int]]:
    """
    Extract SSID and signal strength from the line immediately following BSSID.
    
    Args:
        log_content: List of log lines
        line_num: Line number of the BSSID entry
    
    Returns:
        Tuple of (SSID, signal_strength) or (None, None) if not found
    """
    # Check the next line for SSID info
    if line_num + 1 < len(log_content):
        next_line = log_content[line_num + 1]
        ssid_pattern = re.compile(r'SSID:\s*(.*?)\s*;\s*Signal Strength:\s*(\d+)')
        match = ssid_pattern.search(next_line)
        if match:
            ssid = match.group(1).strip()
            signal = int(match.group(2))
            return ssid, signal
    
    return None, None


def find_gps_in_window(log_content: List[str], target_time: datetime, 
                       start_line: int, window_seconds: int = 2) -> Optional[Dict]:
    """
    Find GPS data within time window around target timestamp.
    
    Args:
        log_content: List of log lines
        target_time: Target timestamp to search around
        start_line: Line number to start searching from
        window_seconds: Search window in seconds (±window_seconds)
    
    Returns:
        Dict with GPS data or None if not found
    """
    gps_pattern = re.compile(
        r'^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}).*'
        r'MM Output: <SD2>Lon:([-\d.]+) Lat:([-\d.]+) Alt:([-\d.]+) Hd:([-\d.]+)</SD2>'
    )
    
    # Search backwards and forwards from the BSSID line
    search_range = range(max(0, start_line - 50), min(len(log_content), start_line + 50))
    
    closest_gps = None
    min_time_diff = timedelta(seconds=window_seconds + 1)
    
    for idx in search_range:
        line = log_content[idx]
        match = gps_pattern.match(line)
        if match:
            gps_time = parse_timestamp(match.group(1))
            time_diff = abs((gps_time - target_time).total_seconds())
            
            if time_diff <= window_seconds and timedelta(seconds=time_diff) < min_time_diff:
                min_time_diff = timedelta(seconds=time_diff)
                closest_gps = {
                    'timestamp': gps_time,
                    'timestamp_str': match.group(1),
                    'mm_lon': float(match.group(2)),
                    'mm_lat': float(match.group(3)),
                    'altitude': float(match.group(4)),
                    'heading': float(match.group(5)),
                    'time_diff': time_diff
                }
    
    return closest_gps


def analyze_log_file(filename: str, target_lat: float, target_lon: float, 
                     max_distance: float = 50.0) -> List[Dict]:
    """
    Analyze a single log file for WiFi networks near target location.
    
    Args:
        filename: Path to log file
        target_lat: Target latitude in decimal degrees
        target_lon: Target longitude in decimal degrees
        max_distance: Maximum distance in meters
    
    Returns:
        List of matching WiFi networks with GPS data
    """
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.readlines()
    except Exception as e:
        print(f"Error reading {filename}: {e}", file=sys.stderr)
        return []
    
    # Extract all BSSID entries
    bssid_entries = extract_bssid_entries(log_content)
    
    matches = []
    for entry in bssid_entries:
        # Get SSID and signal strength
        ssid, signal = extract_ssid_and_signal(log_content, entry['line_num'])
        
        if ssid is None:
            continue
        
        # Find GPS data within time window
        gps_data = find_gps_in_window(log_content, entry['timestamp'], 
                                      entry['line_num'], window_seconds=2)
        
        if gps_data is None:
            continue
        
        # Convert MM coordinates to decimal degrees
        lat, lon = convert_mm_coordinates(gps_data['mm_lon'], gps_data['mm_lat'])
        
        # Calculate distance from target
        distance = haversine_distance(target_lat, target_lon, lat, lon)
        
        # Check if within range
        if distance <= max_distance:
            matches.append({
                'filename': filename,
                'timestamp': entry['timestamp_str'],
                'gps_timestamp': gps_data['timestamp_str'],
                'bssid': entry['bssid'],
                'ssid': ssid,
                'signal_strength': signal,
                'latitude': lat,
                'longitude': lon,
                'mm_lat': gps_data['mm_lat'],
                'mm_lon': gps_data['mm_lon'],
                'altitude': gps_data['altitude'],
                'heading': gps_data['heading'],
                'distance_meters': distance,
                'gps_time_diff': gps_data['time_diff']
            })
    
    return matches


def main():
    parser = argparse.ArgumentParser(
        description='Match WiFi networks to GPS locations from Ford SYNC logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python3 match_wifi_to_GPS_location.py -g "[-XX.XXXXXX, XXX.XXXXXX]" -o results.txt
  python3 match_wifi_to_GPS_location.py -g "[-XX.XXXXXX, XXX.XXXXXX]" -o output.txt
        """
    )
    
    parser.add_argument('-g', '--gps', required=True, type=str,
                       help='GPS coordinates in format [lat, lon] e.g., [-XX.XXXXXX, XXX.XXXXXX]')
    parser.add_argument('-o', '--output', required=True, type=str,
                       help='Output file path')
    parser.add_argument('-d', '--distance', type=float, default=50.0,
                       help='Maximum distance in meters (default: 50)')
    
    args = parser.parse_args()
    
    # Parse GPS coordinates
    try:
        # Remove brackets and split
        gps_str = args.gps.strip('[]')
        lat_str, lon_str = gps_str.split(',')
        target_lat = float(lat_str.strip())
        target_lon = float(lon_str.strip())
    except Exception as e:
        print(f"Error parsing GPS coordinates: {e}", file=sys.stderr)
        print("Format should be: [lat, lon] e.g., [-XX.XXXXXX, XXX.XXXXXX]", file=sys.stderr)
        sys.exit(1)
    
    print(f"Searching for WiFi networks within {args.distance}m of:")
    print(f"  Latitude: {target_lat}")
    print(f"  Longitude: {target_lon}")
    print()
    
    # Find all pas_debug.log* files (matches pas_debug.log, pas_debug.log.1, etc.)
    log_files = glob.glob('pas_debug.log*')
    
    if not log_files:
        print("No pas_debug.log* files found in current directory", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(log_files)} log file(s):")
    for f in sorted(log_files):
        print(f"  - {f}")
    print()
    
    # Analyze each log file
    all_matches = []
    for log_file in sorted(log_files):
        print(f"Analyzing {log_file}...", end=' ')
        matches = analyze_log_file(log_file, target_lat, target_lon, args.distance)
        all_matches.extend(matches)
        print(f"found {len(matches)} match(es)")
    
    print()
    
    # Count unique networks
    unique_networks = set()
    for match in all_matches:
        unique_networks.add((match['bssid'], match['ssid']))
    
    # Write results
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("WiFi Networks Near GPS Location - Analysis Results\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Target GPS Location:\n")
            f.write(f"  Latitude:  {target_lat}\n")
            f.write(f"  Longitude: {target_lon}\n")
            f.write(f"  Search Radius: {args.distance} meters\n\n")
            
            f.write(f"Files Analyzed: {len(log_files)}\n")
            for log_file in sorted(log_files):
                f.write(f"  - {log_file}\n")
            f.write("\n")
            
            f.write(f"Summary:\n")
            f.write(f"  Total WiFi detections within range: {len(all_matches)}\n")
            f.write(f"  Unique WiFi networks (BSSID+SSID): {len(unique_networks)}\n")
            f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("Detected WiFi Networks\n")
            f.write("=" * 80 + "\n\n")
            
            # Sort by distance
            all_matches.sort(key=lambda x: x['distance_meters'])
            
            for idx, match in enumerate(all_matches, 1):
                f.write(f"Match #{idx}:\n")
                f.write(f"  File:              {match['filename']}\n")
                f.write(f"  WiFi Timestamp:    {match['timestamp']}\n")
                f.write(f"  GPS Timestamp:     {match['gps_timestamp']}\n")
                f.write(f"  Time Difference:   {match['gps_time_diff']:.3f} seconds\n")
                f.write(f"  BSSID:             {match['bssid']}\n")
                f.write(f"  SSID:              {match['ssid']}\n")
                f.write(f"  Signal Strength:   {match['signal_strength']}\n")
                f.write(f"  GPS Position:      {match['latitude']:.6f}, {match['longitude']:.6f}\n")
                f.write(f"  MM Coordinates:    Lon:{match['mm_lon']:.6f} Lat:{match['mm_lat']:.6f}\n")
                f.write(f"  Altitude:          {match['altitude']:.1f} m\n")
                f.write(f"  Heading:           {match['heading']:.1f}°\n")
                f.write(f"  Distance:          {match['distance_meters']:.2f} meters\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("Unique SSID Summary\n")
            f.write("=" * 80 + "\n\n")
            
            # Group by SSID (combining all BSSIDs for same SSID)
            ssid_groups = {}
            for match in all_matches:
                ssid = match['ssid'] if match['ssid'] else "(Hidden Network)"
                if ssid not in ssid_groups:
                    ssid_groups[ssid] = []
                ssid_groups[ssid].append(match)
            
            # Sort by detection count (descending)
            sorted_ssids = sorted(ssid_groups.items(), key=lambda x: len(x[1]), reverse=True)
            
            f.write(f"Total unique SSIDs: {len(ssid_groups)}\n")
            f.write(f"Named networks: {len([s for s in ssid_groups.keys() if s != '(Hidden Network)'])}\n")
            f.write(f"Hidden networks: {len(ssid_groups.get('(Hidden Network)', []))}\n\n")
            
            for ssid, detections in sorted_ssids:
                # Get unique BSSIDs for this SSID
                unique_bssids = set(d['bssid'] for d in detections)
                
                f.write(f"SSID: {ssid}\n")
                f.write(f"  Total detections: {len(detections)}\n")
                f.write(f"  Unique BSSIDs: {len(unique_bssids)}\n")
                f.write(f"  Signal strength range: {min(d['signal_strength'] for d in detections)} - "
                       f"{max(d['signal_strength'] for d in detections)}\n")
                f.write(f"  Distance range: {min(d['distance_meters'] for d in detections):.2f}m - "
                       f"{max(d['distance_meters'] for d in detections):.2f}m\n")
                
                # List unique BSSIDs if multiple
                if len(unique_bssids) > 1:
                    f.write(f"  BSSIDs:\n")
                    for bssid in sorted(unique_bssids):
                        bssid_count = len([d for d in detections if d['bssid'] == bssid])
                        f.write(f"    - {bssid} ({bssid_count} detections)\n")
                else:
                    f.write(f"  BSSID: {list(unique_bssids)[0]}\n")
                
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("Unique Networks Summary (by BSSID)\n")
            f.write("=" * 80 + "\n\n")
            
            # Group by unique network (BSSID + SSID combination)
            network_groups = {}
            for match in all_matches:
                key = (match['bssid'], match['ssid'])
                if key not in network_groups:
                    network_groups[key] = []
                network_groups[key].append(match)
            
            for (bssid, ssid), detections in sorted(network_groups.items()):
                f.write(f"Network: {ssid if ssid else '(Hidden)'}\n")
                f.write(f"  BSSID: {bssid}\n")
                f.write(f"  Times detected: {len(detections)}\n")
                f.write(f"  Signal strength range: {min(d['signal_strength'] for d in detections)} - "
                       f"{max(d['signal_strength'] for d in detections)}\n")
                f.write(f"  Distance range: {min(d['distance_meters'] for d in detections):.2f}m - "
                       f"{max(d['distance_meters'] for d in detections):.2f}m\n")
                f.write("\n")
        
        print(f"Results written to: {args.output}")
        print()
        print(f"Summary:")
        print(f"  Files analyzed: {len(log_files)}")
        print(f"  Total detections within {args.distance}m: {len(all_matches)}")
        print(f"  Unique networks: {len(unique_networks)}")
        
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
