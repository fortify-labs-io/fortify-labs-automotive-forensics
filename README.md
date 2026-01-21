# fortify-labs-automotive-forensics
Open-source tools and scripts for automotive forensics and vehicle infotainment system analysis.

# Fortify Labs - Automotive Forensics & Analysis Toolkit

Open-source tools and scripts for automotive forensics and vehicle infotainment system analysis.

---

## About

This repository contains analysis tools developed by [Fortify Labs](https://www.fortifylabs.io/) through real-world automotive cybersecurity research. Our focus is on **evidence-based security assessments** of connected device technology including vehicles, operational technology and membedded systems.

These tools support our mission to provide clarity and confidence in the security of connected assets through proven expertise in system validation and verification.

## Features

### Data Extraction & Analysis
- **GPS Coordinate Extraction** - Parse navigation logs and reconstruct vehicle location history
- **Data Visualization** - Generate KML files for Google Earth and create data visualizations

### Supported Systems
- Ford SYNC 3 (QNX-based)

## Use Cases

- **Digital Forensics** - Vehicle incident investigation and data recovery
- **Cybersecurity Research** - Analysis of automotive attack surfaces and data exposure
- **Privacy Assessments** - Understanding what personal data vehicles collect and retain
- **Incident Reconstruction** - Timeline analysis for accident investigation
- **Security Auditing** - Connected vehicle vulnerability assessment

## Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Clone the Repository

```bash
git clone https://github.com/fortify-labs/automotive-forensics-toolkit.git
cd automotive-forensics-toolkit
```

## Quick Start

```bash
# Extract GPS coordinates from navigation logs
python ford-sync/gps_extractor.py --input unifiedsearch.log --output gps_data.csv

# Analyze Bluetooth connection history
python ford-sync/bluetooth_parser.py --input bt_logs/ --output bt_analysis.json

# Generate KML visualization for Google Earth
python visualization/kml_generator.py --input gps_data.csv --output vehicle_trips.kml
```

## Documentation

For methodology and research context, see our blog series:
- [Behind the Dashboard blog series](https://www.fortifylabs.io/blog/)

## Repository Structure

```
automotive-forensics-toolkit/
├── ford-sync/                              # Ford SYNC-specific analysis tools
│   ├── parse_unifiedsearch_log.py          # GPS extraction and clustering tool
│   ├── parse_unifiedsearch_log_README.md   # Detailed tool documentation
│   └── README.md                           # Ford SYNC tools overview
├── LICENSE
└── README.md                               # Main repository README
```

## Privacy & Ethics

All tools in this repository are designed with privacy protection in mind:

- **No Personal Data** - This repository contains no actual forensic data, GPS coordinates, or personal identifiers
- **Responsible Disclosure** - We follow responsible disclosure practices for security vulnerabilities
- **Educational Purpose** - Tools are intended for legitimate forensic investigation, security research, and privacy assessment

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## About Fortify Labs

[Fortify Labs](https://www.fortifylabs.io/) specializes in evidence-based security for connected technology. We help organizations secure connected assets through proven expertise in:

- **Security and Safety Assessments** - Vulnerability assessments for connected platforms
- **Data Retrieval and Validation** - Advanced techniques for critical data recovery
- **Customized Training** - Specialized technical training in automotive forensics

## Acknowledgments

These tools were developed through research documented in our "Behind the Dashboard" blog series, analyzing data from Ford Ranger PX3 and SYNC 3 systems to understand privacy implications and data retention in modern connected vehicles.

## Disclaimer

These tools are provided for legitimate forensic investigation, security research, and educational purposes only. Users are responsible for ensuring they have appropriate authorization before analyzing any vehicle data. Fortify Labs assumes no liability for misuse of these tools.

---

**Evidence-Based Security for Connected Technology**
