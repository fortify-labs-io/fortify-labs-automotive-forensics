#!/usr/bin/env python3
"""
Ford SYNC Unified Search Log GPS Analysis Tool
Extracts and analyzes GPS coordinates from reverse geocoding entries
"""

import re
import sys
from datetime import datetime
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
from pathlib import Path


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    return c * r


def calculate_centroid(points):
    """
    Calculate the centroid (average) of a list of (lat, lon) points
    """
    if not points:
        return None, None
    
    lat_sum = sum(p[0] for p in points)
    lon_sum = sum(p[1] for p in points)
    count = len(points)
    
    return lat_sum / count, lon_sum / count


def cluster_locations(gps_data, radius_meters=100):
    """
    Cluster GPS points within a specified radius
    Returns list of clusters with their centroid and member points
    """
    clusters = []
    used_indices = set()
    
    for i, (timestamp, lat, lon) in enumerate(gps_data):
        if i in used_indices:
            continue
            
        # Start a new cluster
        cluster_points = [(lat, lon)]
        cluster_timestamps = [timestamp]
        used_indices.add(i)
        
        # Find all points within radius
        for j, (ts, lat2, lon2) in enumerate(gps_data):
            if j in used_indices:
                continue
                
            distance = haversine_distance(lat, lon, lat2, lon2)
            if distance <= radius_meters:
                cluster_points.append((lat2, lon2))
                cluster_timestamps.append(ts)
                used_indices.add(j)
        
        # Calculate centroid
        centroid_lat, centroid_lon = calculate_centroid(cluster_points)
        
        clusters.append({
            'centroid': (centroid_lat, centroid_lon),
            'points': cluster_points,
            'timestamps': cluster_timestamps,
            'count': len(cluster_points)
        })
    
    # Sort by count (most common first)
    clusters.sort(key=lambda x: x['count'], reverse=True)
    return clusters


def parse_log_file(log_file_path):
    """
    Parse the unified search log file and extract GPS coordinates from 2025
    Returns list of tuples: (timestamp, latitude, longitude)
    """
    gps_data = []
    
    # Regex patterns
    timestamp_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
    rgc_pattern = r'rgc=&current_location=(-?\d+\.\d+),(-?\d+\.\d+)&lang='
    
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            current_timestamp = None
            
            for line in f:
                # Check if line starts with System:QNX (entry boundary)
                if line.startswith('System:QNX'):
                    current_timestamp = None
                    continue
                
                # Extract timestamp
                ts_match = re.search(timestamp_pattern, line)
                if ts_match:
                    current_timestamp = ts_match.group(1)
                    continue
                
                # Extract GPS coordinates from rgc= entries
                rgc_match = re.search(rgc_pattern, line)
                if rgc_match and current_timestamp:
                    try:
                        timestamp_obj = datetime.strptime(current_timestamp, '%Y-%m-%d %H:%M:%S')
                        
                        # Only include entries from 2025
                        if timestamp_obj.year == 2025:
                            lat = float(rgc_match.group(1))
                            lon = float(rgc_match.group(2))
                            gps_data.append((current_timestamp, lat, lon))
                    except ValueError:
                        continue
    
    except FileNotFoundError:
        print(f"Error: File '{log_file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    return gps_data


def generate_google_maps_url(lat, lon):
    """Generate Google Maps URL for given coordinates"""
    return f"https://www.google.com/maps?q={lat},{lon}"


def format_coordinate(lat, lon):
    """Format coordinates for display"""
    lat_dir = 'N' if lat >= 0 else 'S'
    lon_dir = 'E' if lon >= 0 else 'W'
    return f"{abs(lat):.6f}°{lat_dir}, {abs(lon):.6f}°{lon_dir}"


def save_all_points(gps_data, output_file):
    """Save all GPS points to output log file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# GPS Points from 2025 - Unified Search Log Analysis\n")
        f.write("# Format: Timestamp | Latitude | Longitude\n")
        f.write("=" * 80 + "\n\n")
        
        for timestamp, lat, lon in gps_data:
            f.write(f"{timestamp} | {lat:.6f} | {lon:.6f}\n")
    
    print(f"✓ Saved all {len(gps_data)} GPS points to: {output_file}")


def generate_report(gps_data, clusters, output_file):
    """Generate the formatted analysis report"""
    
    if not gps_data:
        print("No GPS data found for 2025")
        return
    
    # Get date range
    timestamps = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts, _, _ in gps_data]
    first_date = min(timestamps)
    last_date = max(timestamps)
    
    # Calculate statistics
    total_points = len(gps_data)
    unique_clusters = len(clusters)
    
    # Get top 3 clusters
    top_3 = clusters[:3] if len(clusters) >= 3 else clusters
    
    # Calculate combined stats
    top_3_total = sum(c['count'] for c in top_3)
    top_3_percent = (top_3_total / total_points * 100) if total_points > 0 else 0
    other_points = total_points - top_3_total
    other_percent = (other_points / total_points * 100) if total_points > 0 else 0
    
    # Generate report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("GPS LOCATION ANALYSIS REPORT - 2025\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total GPS Points: {total_points}\n")
        f.write(f"Unique Locations (clustered): {unique_clusters}\n\n")
        
        f.write("TOP 3 MOST COMMON LOCATIONS\n")
        f.write("-" * 80 + "\n\n")
        
        for idx, cluster in enumerate(top_3, 1):
            centroid_lat, centroid_lon = cluster['centroid']
            timestamps_sorted = sorted(cluster['timestamps'])
            first_visit = timestamps_sorted[0]
            last_visit = timestamps_sorted[-1]
            count = cluster['count']
            percentage = (count / total_points * 100) if total_points > 0 else 0
            
            f.write(f"LOCATION #{idx}\n")
            f.write(f"  Coordinates: {format_coordinate(centroid_lat, centroid_lon)}\n")
            f.write(f"  Clustered around: [{centroid_lat:.6f}, {centroid_lon:.6f}]\n")
            f.write(f"  Total Points: {count} ({percentage:.1f}% of all points)\n")
            f.write(f"  First Visit: {first_visit}\n")
            f.write(f"  Last Visit: {last_visit}\n")
            f.write(f"  Google Maps: {generate_google_maps_url(centroid_lat, centroid_lon)}\n\n")
        
        f.write("COMBINED STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Top 3 locations combined: {top_3_total} points ({top_3_percent:.1f}%)\n")
        f.write(f"Other locations: {other_points} points ({other_percent:.1f}%)\n\n")
        
        f.write("ADDITIONAL DETAILS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Date range: {first_date.strftime('%Y-%m-%d %H:%M:%S')} to {last_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Clustering precision: ~100 meters\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✓ Generated analysis report: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_unifiedsearch_log.py <log_file_path>")
        print("\nExample:")
        print("  python parse_unifiedsearch_log.py unifiedsearch.log")
        sys.exit(1)
    
    log_file_path = sys.argv[1]
    
    print(f"Parsing log file: {log_file_path}")
    print("Extracting GPS coordinates from 2025...")
    
    # Parse log file
    gps_data = parse_log_file(log_file_path)
    
    if not gps_data:
        print("\n⚠ No GPS coordinates found for 2025 in the log file.")
        sys.exit(0)
    
    print(f"✓ Found {len(gps_data)} GPS points from 2025")
    
    # Save all points to output log
    all_points_file = "AI-analysis_unifiedsearch-log.log"
    save_all_points(gps_data, all_points_file)
    
    # Cluster locations
    print("\nClustering locations (100m radius)...")
    clusters = cluster_locations(gps_data, radius_meters=100)
    print(f"✓ Identified {len(clusters)} unique location clusters")
    
    # Generate report
    report_file = "GPS_Location_Analysis_Report_2025.txt"
    print("\nGenerating analysis report...")
    generate_report(gps_data, clusters, report_file)
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)
    print(f"\nOutput files:")
    print(f"  1. {report_file} - Formatted analysis report")
    print(f"  2. {all_points_file} - All GPS points with timestamps")


if __name__ == "__main__":
    main()
