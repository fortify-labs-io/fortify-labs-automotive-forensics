# Ford SYNC Tools

Analysis tools for Ford SYNC 3 infotainment systems developed through automotive cybersecurity research at Fortify Labs.

## Available Tools

### parse_unifiedsearch_log.py
GPS location analysis tool that extracts and clusters GPS coordinates from Ford SYNC unified search logs.

**Features:**
- Parses Ford SYNC unified search log files (System:QNX format)
- Extracts GPS coordinates from reverse geocoding entries
- Clusters locations within 100-meter radius using Haversine distance
- Identifies most frequently visited locations
- Generates analysis reports with timestamps and statistics

**Quick Start:**
```bash
python parse_unifiedsearch_log.py unifiedsearch.log
```

See detailed documentation in [parse_unifiedsearch_log_README.md](parse_unifiedsearch_log_README.md)

## Supported Systems

- Ford SYNC 3 (QNX-based)
- Ford Ranger PX3

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Use Cases

- Digital forensics investigations
- Privacy research (understanding vehicle data collection)
- Travel pattern analysis
- Incident reconstruction
- Vehicle usage auditing

## Privacy & Ethics

These tools are designed for legitimate forensic investigation and security research:

- ⚠️ **Always redact GPS coordinates** before publishing research
- ⚠️ **Obtain proper authorization** before analyzing vehicle data
- ⚠️ **Respect privacy** - use generic location names in public documentation

## Related Research

These tools support the analysis documented in the [Behind the Dashboard blog series](https://www.fortifylabs.io/blog/):

## License

These tools are provided for legitimate automotive security research and forensic analysis purposes only.

## About Fortify Labs

[Fortify Labs](https://www.fortifylabs.io/) - Evidence-Based Security for Connected Technology
