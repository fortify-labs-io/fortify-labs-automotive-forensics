# JSON Formatter

Simple utility to format minified/single-line JSON files with proper indentation for easier viewing and analysis.

## Usage

```bash
python3 convert-to-json_ccl-files.py -i input.txt -o output.json
```

## What It Does

- Reads a JSON file (minified or formatted)
- Outputs a properly indented version with 2-space indentation
- Makes large JSON files human-readable

## Examples

**Basic usage:**
```bash
python3 convert-to-json_ccl-files.py -i 00000_zip.txt -o 00000_zip_formatted.json
```

## Requirements

- Python 3.x (standard library only)
- Valid JSON input file

## Common Use Cases

- Formatting Ford SYNC CCL (Cloud Connected Logs) batch files
- Making API response data readable
- Preparing JSON for manual analysis
- Converting single-line JSON to multi-line format

## Author
Created for automotive cybersecurity research and forensic analysis at Fortify Labs.

## License
This tool is provided for legitimate automotive security research and forensic analysis purposes.
