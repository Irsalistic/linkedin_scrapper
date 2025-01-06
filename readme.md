# LinkedIn Email Extractor and Validator

This Python script automates the process of extracting company details and employee email addresses from LinkedIn and validates those emails using a third-party service. It uses **Selenium** for web scraping and interaction with LinkedIn, and includes functionality for generating potential email addresses based on company and employee data.

---

## Features

- **LinkedIn Login:** Automates login using credentials stored in environment variables.
- **Company Search:** Searches for companies on LinkedIn based on keywords.
- **Data Extraction:**
  - Extracts company information (e.g., website, contact details).
  - Scrapes employee names and generates potential email addresses.
- **Email Validation:** Validates emails using the `email_validator1_script` and `ZeroBounce` API.
- **Output Storage:** Stores valid emails in a CSV file.

---

## Prerequisites

1. **Python 3.10 or higher**  
2. **Chrome Browser**  
3. **Selenium WebDriver** (managed by `webdriver-manager`)  
4. **LinkedIn Account** with valid login credentials.  
5. **ZeroBounce API Key** for email validation.

---

## Installation

1. Clone this repository:

2. Move to the clone directory

3. Install required dependencies:
```bash
pip install -r requirements.txt
```
4. Create a .env file for sensitive data:

- zero_bounce_api_key=<your_zero_bounce_api_key>
- linkedin_email=<your_linkedin_email>
- linkedin_keys=<your_linkedin_password>

### Usage
```bash
python linkedin_scrapper.py
```

