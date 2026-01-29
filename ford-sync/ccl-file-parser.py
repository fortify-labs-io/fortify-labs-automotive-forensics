#!/usr/bin/env python3
"""
Ford SYNC Telemetry Timeline Analyzer
======================================
Analyzes Ford SYNC Cloud Analytics telemetry files and generates timeline reports.
Usage:
    python analyze_telemetry.py -i input_file.txt -o report.md
    python analyze_telemetry.py --input telemetry.json --output timeline.txt --format txt
"""
import json
import argparse
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

class TelemetryAnalyzer:
    """Analyzes Ford SYNC telemetry data and generates timeline reports."""
    
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = None
        self.header = None
        self.boot_sessions = defaultdict(list)
        
    def load_data(self):
        """Load and parse JSON telemetry file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.header = self.data.get('header', {})
            print(f"✓ Successfully loaded telemetry file: {self.input_file}")
            return True
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON format - {e}")
            return False
        except FileNotFoundError:
            print(f"✗ Error: File not found - {self.input_file}")
            return False
        except Exception as e:
            print(f"✗ Error loading file: {e}")
            return False
    
    def organize_by_boot(self):
        """Organize all events by boot session."""
        if not self.data:
            return False
            
        for batch in self.data.get('batchevents', []):
            appbatch = batch.get('appbatch', {})
            appname = appbatch.get('appname', 'unknown')
            
            for event in appbatch.get('appevents', []):
                bootcount = event.get('bootcount', 'unknown')
                event['_appname'] = appname  # Add app name to event
                self.boot_sessions[bootcount].append(event)
        
        # Sort events within each boot by uptime
        for bootcount in self.boot_sessions:
            self.boot_sessions[bootcount].sort(key=lambda x: int(x.get('uptime', 0)))
        
        print(f"✓ Organized {sum(len(events) for events in self.boot_sessions.values())} events into {len(self.boot_sessions)} boot sessions")
        return True
    
    def analyze_boot_session(self, bootcount):
        """Analyze a single boot session and return summary data."""
        events = self.boot_sessions[bootcount]
        if not events:
            return None
        
        # Get time range - filter events that have time field
        events_with_time = [e for e in events if 'time' in e]
        if not events_with_time:
            return None
        
        first_event = events_with_time[0]
        last_event = events_with_time[-1]
        
        start_time = datetime.fromtimestamp(int(first_event['time']) / 1000)
        end_time = datetime.fromtimestamp(int(last_event['time']) / 1000)
        
        # Calculate duration from uptime if available, otherwise from timestamps
        if 'uptime' in last_event and 'uptime' in first_event:
            duration_ms = int(last_event['uptime']) - int(first_event['uptime'])
        else:
            duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Analyze ignition states
        ignition_changes = [e for e in events if e.get('category') == 'ignitionState']
        ignition_sequence = []
        for ig in ignition_changes:
            ignition_sequence.append({
                'from': ig.get('prevStatus', 'unknown'),
                'to': ig.get('status', 'unknown'),
                'uptime': ig.get('uptime', 0),
                'time': datetime.fromtimestamp(int(ig['time']) / 1000)
            })
        
        # Analyze gear changes
        gear_changes = [e for e in events if e.get('category') == 'gear']
        gear_sequence = []
        for gear in gear_changes:
            gear_sequence.append({
                'from': gear.get('prevGear', 'init'),
                'to': gear.get('gear', 'unknown'),
                'uptime': gear.get('uptime', 0),
                'time': datetime.fromtimestamp(int(gear['time']) / 1000)
            })
        
        # Analyze navigation
        nav_events = [e for e in events if e.get('category') == 'nav']
        nav_active_time = 0
        nav_activations = []
        
        for nav in nav_events:
            prop = nav.get('property', '')
            value = nav.get('value', '')
            
            if prop == 'isNavActive':
                if isinstance(value, str) and value == 'started':
                    nav_activations.append({
                        'type': 'activation',
                        'time': datetime.fromtimestamp(int(nav['time']) / 1000),
                        'uptime': nav.get('uptime', 0)
                    })
                elif isinstance(value, (int, str)) and str(value).isdigit():
                    duration = int(value)
                    nav_active_time += duration
                    nav_activations.append({
                        'type': 'duration',
                        'duration_ms': duration,
                        'time': datetime.fromtimestamp(int(nav['time']) / 1000)
                    })
        
        # Analyze door activity
        door_events = [e for e in events if e.get('category') == 'driverDoorStatus']
        door_sequence = []
        for door in door_events:
            door_sequence.append({
                'status': door.get('status', 'unknown'),
                'uptime': door.get('uptime', 0),
                'time': datetime.fromtimestamp(int(door['time']) / 1000)
            })
        
        # Get speed data
        speeds = [float(e.get('speed', 0)) for e in events if 'speed' in e]
        max_speed = max(speeds) if speeds else 0.0
        
        # Check for errors
        errors = [e for e in events if 'error' in e.get('category', '').lower() or 
                  'fatal' in e.get('category', '').lower()]
        
        return {
            'bootcount': bootcount,
            'start_time': start_time,
            'end_time': end_time,
            'duration_ms': duration_ms,
            'duration_seconds': duration_ms / 1000,
            'total_events': len(events),
            'ignition_sequence': ignition_sequence,
            'gear_sequence': gear_sequence,
            'door_sequence': door_sequence,
            'nav_active_time_ms': nav_active_time,
            'nav_activations': nav_activations,
            'max_speed': max_speed,
            'errors': errors
        }
    
    def generate_markdown_report(self):
        """Generate markdown formatted timeline report."""
        if not self.boot_sessions:
            return "No boot sessions found in telemetry file."
        
        report = []
        report.append("# Ford SYNC Telemetry Timeline Analysis")
        report.append(f"\n**File:** {Path(self.input_file).name}")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n---\n")
        
        # Vehicle Information
        report.append("## Vehicle Information\n")
        report.append(f"- **VIN:** {self.header.get('vininfo', 'N/A')}")
        report.append(f"- **Region:** {self.header.get('region', 'N/A')}")
        report.append(f"- **Odometer:** {self.header.get('odometer', 'N/A')} km")
        report.append(f"- **Fuel Level:** {self.header.get('fuellevel', 'N/A')}%")
        report.append(f"- **Navigation:** {self.header.get('navigation', 'N/A')}")
        report.append(f"- **Build:** {self.header.get('build', 'N/A')}")
        report.append(f"- **Batch Sequence:** {self.header.get('batchsequence', 'N/A')}")
        report.append("\n---\n")
        
        # Timeline Analysis
        report.append("## Timeline Analysis - Boot Sessions\n")
        
        for bootcount in sorted(self.boot_sessions.keys(), key=lambda x: str(x)):
            analysis = self.analyze_boot_session(bootcount)
            if not analysis:
                continue
            
            report.append(f"### Boot {bootcount} ({analysis['start_time'].strftime('%H:%M:%S')} - {analysis['end_time'].strftime('%H:%M:%S')})\n")
            
            # Duration
            duration_str = self._format_duration(analysis['duration_ms'])
            report.append(f"**Duration:** {duration_str}")
            
            # Ignition sequence
            if analysis['ignition_sequence']:
                ign_states = [ig['to'] for ig in analysis['ignition_sequence']]
                initial = analysis['ignition_sequence'][0]['from']
                if initial == 'undefined':
                    initial = 'OFF'
                report.append(f"**Ignition:** {initial} → {' → '.join(ign_states)}")
            else:
                report.append("**Ignition:** No changes recorded")
            
            # Activity summary
            report.append(f"**Activity:**")
            
            # Door activity
            if analysis['door_sequence']:
                door_changes = [f"{d['status']}" for d in analysis['door_sequence']]
                report.append(f"  - Driver door: {' → '.join(door_changes)}")
            
            # Gear changes
            if analysis['gear_sequence']:
                gear_str = self._format_gear_sequence(analysis['gear_sequence'])
                report.append(f"  - Gear changes: {gear_str}")
                report.append(f"  - Total gear changes: {len(analysis['gear_sequence'])}")
            else:
                report.append(f"  - No gear changes recorded")
            
            # Speed
            if analysis['max_speed'] > 0:
                report.append(f"  - Maximum speed: {analysis['max_speed']:.2f} km/h")
            else:
                report.append(f"  - Vehicle stationary")
            
            # Navigation
            if analysis['nav_active_time_ms'] > 0:
                nav_time = self._format_duration(analysis['nav_active_time_ms'])
                report.append(f"**Navigation:** Active for {nav_time}")
            elif analysis['nav_activations']:
                report.append(f"**Navigation:** {len(analysis['nav_activations'])} activation(s)")
            else:
                report.append(f"**Navigation:** Not active")
            
            # Errors
            if analysis['errors']:
                report.append(f"**⚠️ Errors:** {len(analysis['errors'])} error(s) detected")
            
            # Event count
            report.append(f"**Total Events:** {analysis['total_events']}")
            
            # Outcome/interpretation
            report.append(f"**Outcome:** {self._interpret_session(analysis)}")
            
            report.append("")  # Blank line between sessions
        
        # Summary statistics
        report.append("\n---\n")
        report.append("## Summary Statistics\n")
        
        total_events = sum(len(events) for events in self.boot_sessions.values())
        total_gear_changes = sum(len([e for e in self.boot_sessions[b] if e.get('category') == 'gear']) 
                                 for b in self.boot_sessions)
        total_nav_time = sum(self.analyze_boot_session(b)['nav_active_time_ms'] 
                            for b in self.boot_sessions if self.analyze_boot_session(b))
        
        report.append(f"- **Total Boot Sessions:** {len(self.boot_sessions)}")
        report.append(f"- **Total Events:** {total_events}")
        report.append(f"- **Total Gear Changes:** {total_gear_changes}")
        report.append(f"- **Total Navigation Time:** {self._format_duration(total_nav_time)}")
        
        # Time span
        all_times = []
        for bootcount in self.boot_sessions:
            analysis = self.analyze_boot_session(bootcount)
            if analysis:
                all_times.append(analysis['start_time'])
                all_times.append(analysis['end_time'])
        
        if all_times:
            time_span = max(all_times) - min(all_times)
            report.append(f"- **Time Span:** {self._format_timedelta(time_span)}")
        
        return "\n".join(report)
    
    def generate_text_report(self):
        """Generate plain text formatted timeline report."""
        if not self.boot_sessions:
            return "No boot sessions found in telemetry file."
        
        report = []
        report.append("=" * 70)
        report.append("FORD SYNC TELEMETRY TIMELINE ANALYSIS")
        report.append("=" * 70)
        report.append(f"File: {Path(self.input_file).name}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")
        
        # Vehicle Information
        report.append("VEHICLE INFORMATION")
        report.append("-" * 70)
        report.append(f"VIN:           {self.header.get('vininfo', 'N/A')}")
        report.append(f"Region:        {self.header.get('region', 'N/A')}")
        report.append(f"Odometer:      {self.header.get('odometer', 'N/A')} km")
        report.append(f"Fuel Level:    {self.header.get('fuellevel', 'N/A')}%")
        report.append(f"Navigation:    {self.header.get('navigation', 'N/A')}")
        report.append(f"Build:         {self.header.get('build', 'N/A')}")
        report.append("")
        
        # Timeline Analysis
        report.append("TIMELINE ANALYSIS - BOOT SESSIONS")
        report.append("=" * 70)
        
        for bootcount in sorted(self.boot_sessions.keys(), key=lambda x: str(x)):
            analysis = self.analyze_boot_session(bootcount)
            if not analysis:
                continue
            
            report.append("")
            report.append(f"Boot {bootcount}: {analysis['start_time'].strftime('%H:%M:%S')} - {analysis['end_time'].strftime('%H:%M:%S')}")
            report.append("-" * 70)
            
            duration_str = self._format_duration(analysis['duration_ms'])
            report.append(f"Duration:      {duration_str}")
            
            # Ignition
            if analysis['ignition_sequence']:
                ign_states = [ig['to'] for ig in analysis['ignition_sequence']]
                initial = analysis['ignition_sequence'][0]['from']
                if initial == 'undefined':
                    initial = 'OFF'
                report.append(f"Ignition:      {initial} → {' → '.join(ign_states)}")
            
            # Activity
            report.append("Activity:")
            
            if analysis['door_sequence']:
                door_changes = [f"{d['status']}" for d in analysis['door_sequence']]
                report.append(f"  - Driver door: {' → '.join(door_changes)}")
            
            if analysis['gear_sequence']:
                gear_str = self._format_gear_sequence(analysis['gear_sequence'])
                report.append(f"  - Gear changes: {gear_str}")
                report.append(f"  - Total gear changes: {len(analysis['gear_sequence'])}")
            
            if analysis['max_speed'] > 0:
                report.append(f"  - Maximum speed: {analysis['max_speed']:.2f} km/h")
            else:
                report.append(f"  - Vehicle stationary")
            
            # Navigation
            if analysis['nav_active_time_ms'] > 0:
                nav_time = self._format_duration(analysis['nav_active_time_ms'])
                report.append(f"Navigation:    Active for {nav_time}")
            elif analysis['nav_activations']:
                report.append(f"Navigation:    {len(analysis['nav_activations'])} activation(s)")
            
            # Errors
            if analysis['errors']:
                report.append(f"Errors:        {len(analysis['errors'])} error(s) detected")
            
            report.append(f"Total Events:  {analysis['total_events']}")
            report.append(f"Outcome:       {self._interpret_session(analysis)}")
        
        report.append("")
        report.append("=" * 70)
        report.append("SUMMARY STATISTICS")
        report.append("=" * 70)
        
        total_events = sum(len(events) for events in self.boot_sessions.values())
        total_gear_changes = sum(len([e for e in self.boot_sessions[b] if e.get('category') == 'gear']) 
                                 for b in self.boot_sessions)
        total_nav_time = sum(self.analyze_boot_session(b)['nav_active_time_ms'] 
                            for b in self.boot_sessions if self.analyze_boot_session(b))
        
        report.append(f"Total Boot Sessions:    {len(self.boot_sessions)}")
        report.append(f"Total Events:           {total_events}")
        report.append(f"Total Gear Changes:     {total_gear_changes}")
        report.append(f"Total Navigation Time:  {self._format_duration(total_nav_time)}")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def _format_duration(self, ms):
        """Format milliseconds as human-readable duration."""
        seconds = ms / 1000
        
        if seconds < 60:
            return f"~{int(seconds)} seconds"
        
        minutes = int(seconds / 60)
        remaining_seconds = int(seconds % 60)
        
        if minutes < 60:
            return f"~{minutes} min {remaining_seconds} sec"
        
        hours = int(minutes / 60)
        remaining_minutes = minutes % 60
        return f"~{hours} hr {remaining_minutes} min"
    
    def _format_timedelta(self, td):
        """Format timedelta as human-readable string."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours} hour" + ("s" if hours != 1 else ""))
        if minutes > 0:
            parts.append(f"{minutes} minute" + ("s" if minutes != 1 else ""))
        if seconds > 0 or not parts:
            parts.append(f"{seconds} second" + ("s" if seconds != 1 else ""))
        
        return ", ".join(parts)
    
    def _format_gear_sequence(self, gear_sequence):
        """Format gear changes as a readable string."""
        if not gear_sequence:
            return "None"
        
        gears = []
        for gear in gear_sequence:
            from_gear = gear['from']
            to_gear = gear['to']
            if from_gear != 'init':
                gears.append(f"{from_gear}→{to_gear}")
            else:
                gears.append(to_gear)
        
        return ", ".join(gears)
    
    def _interpret_session(self, analysis):
        """Provide interpretation of what happened in this boot session."""
        gear_count = len(analysis['gear_sequence'])
        nav_time = analysis['nav_active_time_ms']
        max_speed = analysis['max_speed']
        
        # Check final ignition state
        final_ignition = 'unknown'
        if analysis['ignition_sequence']:
            final_ignition = analysis['ignition_sequence'][-1]['to']
        
        # Extensive gear changes
        if gear_count >= 5:
            return "Extensive parking/maneuvering activity"
        
        # Some gear changes with navigation
        if gear_count >= 2 and nav_time > 10000:
            if max_speed > 1.0:
                return "Short driving session with navigation"
            else:
                return "Parking with navigation active"
        
        # No movement
        if gear_count == 0 and max_speed == 0:
            if final_ignition == 'off':
                return "System shutdown/sleep"
            else:
                return "Stationary with ignition on"
        
        # Brief session
        if analysis['duration_seconds'] < 30:
            return "Brief session - quick start/stop"
        
        # Default
        if final_ignition == 'off':
            return "Normal shutdown"
        else:
            return "Session in progress"

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Analyze Ford SYNC telemetry files and generate timeline reports.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i telemetry.txt -o report.md
  %(prog)s --input data.json --output timeline.txt --format txt
  %(prog)s -i telemetry.txt -o report.md --format markdown
        """
    )
    
    parser.add_argument('-i', '--input', required=True,
                       help='Input telemetry file (JSON format)')
    parser.add_argument('-o', '--output', required=True,
                       help='Output report file')
    parser.add_argument('-f', '--format', choices=['markdown', 'txt', 'md'],
                       default='markdown',
                       help='Output format (default: markdown)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output during processing')
    
    args = parser.parse_args()
    
    # Normalize format
    output_format = 'markdown' if args.format == 'md' else args.format
    
    print(f"\nFord SYNC Telemetry Timeline Analyzer")
    print(f"{'=' * 50}\n")
    
    # Initialize analyzer
    analyzer = TelemetryAnalyzer(args.input)
    
    # Load data
    if not analyzer.load_data():
        sys.exit(1)
    
    # Organize by boot sessions
    if not analyzer.organize_by_boot():
        print("✗ Error: No boot sessions found")
        sys.exit(1)
    
    # Generate report
    print(f"⚙ Generating {output_format} report...")
    
    if output_format == 'markdown':
        report = analyzer.generate_markdown_report()
    else:
        report = analyzer.generate_text_report()
    
    # Write output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ Report successfully written to: {args.output}")
        print(f"  - Boot sessions analyzed: {len(analyzer.boot_sessions)}")
        print(f"  - Total events processed: {sum(len(e) for e in analyzer.boot_sessions.values())}")
        print(f"\nDone!")
    except Exception as e:
        print(f"✗ Error writing output file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
