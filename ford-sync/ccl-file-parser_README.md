# Ford SYNC Telemetry Timeline Analyzer

Simple utility to analyze Ford SYNC Cloud Analytics telemetry files and generate timeline reports showing boot sessions, vehicle activity, and system events.

## Usage

```bash
python3 ccl-file-parser.py -i input_file.txt -o report.md
```

## What It Does

- Reads Ford SYNC telemetry data (JSON format)
- Organizes events by boot session
- Analyzes ignition states, gear changes, navigation usage, and door activity
- Generates timeline reports showing vehicle usage patterns
- Provides human-readable interpretations of each session

## Examples

**Basic usage:**

```bash
python3 ccl-file-parser.py -i telemetry.json -o timeline_report.md
```

**Generate plain text format:**

```bash
python3 ccl-file-parser.py -i telemetry.json -o timeline_report.txt --format txt
```

**Verbose output:**

```bash
python3 ccl-file-parser.py -i telemetry.json -o report.md --verbose
```

## Requirements

- Python 3.x (standard library only)
- Valid Ford SYNC telemetry JSON file

## Common Use Cases

- Analyzing Ford SYNC Cloud Connected Logs (CCL) batch files
- Generating human-readable timeline reports from telemetry data
- Understanding vehicle usage patterns and boot session sequences
- Identifying navigation usage and driving activity
- Forensic analysis of Ford vehicle telemetry data

## Author

Created for automotive cybersecurity research and forensic analysis at Fortify Labs.

## License

This tool is provided for legitimate automotive security research and forensic analysis purposes.
