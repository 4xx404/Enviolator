# Enviolator

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**Enviolator** is a web reconnaissance and security assessment tool developed in Python 3, designed to detect and extract exposed .env files from target websites. These files often contain sensitive configuration details such as API keys, database credentials, and authentication secrets.

This tool automates the discovery of .env files and displays their contents in a structured format, assisting security researchers and penetration testers in identifying potential misconfigurations.

---

## Features
- Attempts to locate .env files on the target host.
- Parses and extracts all key-value pairs found in the .env file.
- Highlights common sensitive entries such as DB_PASSWORD, API_KEY, SECRET_KEY, etc.
- Supports both single-target and bulk-target scanning.
- Saves extracted data for later analysis.
- Lightweight and fast, with configurable request handling.

---

## Output

Output

All results are saved in the following directory structure: ```Results/```

---

### Usage

```bash
cd Enviolator
python3 -m pip install -r requirements.txt
sudo chmod +x Enviolator.py
python3 Enviolator.py
```

You will be prompted to enter either a single host URL or a list of URLs. The tool will then:

Attempt to retrieve the .env file from the target.
Parse and display extracted key-value pairs.
Save results in a structured output directory for further review.

### Requirements

- Python 3.8+
- Internet access (for retrieving target .env files)
- Dependencies listed in requirements.txt

Install required packages with:
```pip install -r requirements.txt```

### Disclaimer
See [Enviolator Disclaimer](https://github.com/4xx404/Enviolator/blob/master/DISCLAIMER.md)
