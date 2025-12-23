# ⚠️ Disclaimer

This project is provided **for educational purposes only**. The author **does not condone or encourage** scraping Doctolib or any other website in violation of their terms of service. Use of this code to scrape real websites is done **entirely at your own risk**, and the author **cannot be held responsible** for any legal or other consequences that may arise. This repository is intended solely to demonstrate web scraping techniques and Selenium usage in a safe, controlled environment.

# scraptolib

**scraptolib** is a Python package for scraping practitioner profiles and listings on popular online healthcare directories.  
It provides classes to retrieve detailed practitioner information, establishments, fees, languages, history, and more.

---

## Table of Contents

- [Features](#features)  
- [Installation](#installation)
- [Examples](#examples)

---

## Features

- Scrape practitioner cards (`CardsScraper`)  
- Scrape detailed practitioner profiles (`ProfileScraper`)  
- Automatic Chrome driver management (start/stop)  
- Handle cookies and temporary errors ("Retry later")  
- Extract key information:  
  - Name, specialty, address  
  - Spoken languages  
  - Skills / expertise  
  - Summary / biography  
  - Prices
  - History and associations  
  - Website and contact details  

---

## Installation 
### Driver
Download your chromedriver through the following [link](https://developer.chrome.com/docs/chromedriver?hl=en)

### Install the package with uv
1. Clone the repo
```bash
git clone https://github.com/<username>/scraptolib.git
```

2. Install uv with your package manager _example for pip_
```bash
pip install uv
```

3. Create your venv and install dependancies
```bash
uv venv
uv sync
```

4. Install scraptolib
Run this command at the root of your project (where pyproject.toml is)
```bash
uv pip install .
```

### Install the package with pip


## Examples
Please refer yourself to the _examples_ folder. 
You will find examples of use for CardsScraper and ProfileScraper.
