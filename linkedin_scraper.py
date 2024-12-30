
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
from email_validator1_script import *
import csv

load_dotenv()

# Output file setup
output_file = "valid_emails.csv"
if not os.path.exists(output_file):
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Email"])  # Header
valid_emails = []

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Environment variables
zero_bounce_api_key = os.getenv("zero_bounce_api_key")
linkedin_email = os.getenv("linkedin_email")
linkedin_password = os.getenv("linkedin_keys")

# Login to LinkedIn
driver.get("https://www.linkedin.com/login")
try:
    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
    username.send_keys(linkedin_email)
    password.send_keys(linkedin_password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)
except Exception as e:
    print(f"Login failed: {e}")
    driver.quit()
    exit()

# Search for "ERP Solutions"
try:
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search']")))
    search_box.send_keys("Billing")
    search_box.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Companies']"))).click()
    time.sleep(3)
    companies_page_url = driver.current_url
    print(f"companies_page_url:{companies_page_url}")
except Exception as e:
    print(f"Search setup failed: {e}")
    driver.quit()
    exit()

# Iterate over companies
try:
    while True:
        # companies = WebDriverWait(driver, 20).until(
        #     EC.presence_of_all_elements_located((By.XPATH, '//*[@id="HxHMRnZeQSesXi8t/CsNfg=="]/div/ul/li[1]'))
        # )
        # companies = driver.find_elements(By.XPATH, '//*[@id="HxHMRnZeQSesXi8t/CsNfg=="]/div/ul/li[1]')

        for index in range(10):
            try:
                company_list = driver.find_element(By.XPATH, "//ul[@role='list']")
                companies = company_list.find_elements(By.TAG_NAME, "li")
                # companies = driver.find_elements(By.XPATH, '//*[@id="HxHMRnZeQSesXi8t/CsNfg=="]/div/ul/li[1]')
                # Scroll to make the company visible
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", companies[index])
                time.sleep(3)

                companies[index].find_element(By.TAG_NAME, "a").click()
                time.sleep(3)

                # Navigate to About section
                try:
                    about_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/about/')]"))
                    )
                    about_link.click()
                    time.sleep(2)
                except Exception:
                    print("About section not found, skipping...")
                    driver.back()
                    continue

                # Scroll to load all content
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                # Extract company details
                company_infos_titles = [elem.text for elem in driver.find_elements(By.XPATH,
                                                                                   "//dt[@class='mb1']/h3[@class='text-heading-medium']")]
                company_infos = [elem.text for elem in driver.find_elements(By.XPATH, "//dd[contains(@class, 'mb4')]")]
                matched_info = dict(zip(company_infos_titles, company_infos))
                print(f"Company Details: {matched_info}")

                # Navigate to People section
                try:
                    people_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/people/')]"))
                    )
                    people_link.click()
                    time.sleep(3)

                    search_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//input[@placeholder='Search employees by title, keyword or school']"))
                    )
                    search_box.clear()
                    search_box.send_keys("Founder, CEO, Managing Director, CTO, Director")
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(3)

                    matches = driver.find_elements(By.CSS_SELECTOR, "div.t-black")
                    for match in matches:
                        name = match.text
                        if name and name != "LinkedIn Member":
                            domain = matched_info.get("Website", "")
                            if not domain:
                                domain = "example.com"
                            possible_emails = generate_emails(name, domain)
                            print(f"\nPossible Emails for {name}: {possible_emails}")

                            for email in possible_emails:
                                with open(output_file, mode="a", newline="", encoding="utf-8") as file:
                                    writer = csv.writer(file)
                                    writer.writerow([email])
                                is_valid = validate_email(
                                    email_address=email,
                                    check_format=True,
                                    check_blacklist=True,
                                    check_dns=True,
                                    dns_timeout=10,
                                    check_smtp=True,
                                    smtp_timout=10,
                                    smtp_helo_host="my.host.name",
                                    smtp_from_address='my@from.addr.ess',
                                    smtp_skip_tls=False,
                                    smtp_tls_context=False,
                                    address_types=frozenset([IPv4Address, IPv6Address]))
                                if is_valid == "valid":
                                    valid_emails.append(email)
                                    print(f"Valid Email: {email}")
                                    break

                except Exception as e:
                    print(f"Error in People section: {e}")
            except Exception as e:
                print(f"Error processing company {index}: {e}")
            finally:
                # Navigate back to the main results
                # for _ in range(4):
                #     driver.back()
                #     time.sleep(3)
                driver.get(companies_page_url)
                time.sleep(5)

        # Go to next page
        try:
            # Scroll to load all content
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            # Wait for the Next button to be clickable
            next_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
            )

            # Scroll the button into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(0.5)

            # Check if the button is enabled
            if not next_button.is_enabled():
                print("Next button is disabled.")
                break

            # Click the Next button
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)

            # Capture the current URL for debugging or processing
            companies_page_url = driver.current_url
            print("Navigated to:", companies_page_url)

        except Exception as e:
            print(f"Error occurred: {e}")
            break

except Exception as e:
    print(f"Error during company iteration: {e}")

# Close WebDriver
driver.quit()

# Output collected emails
print("All Valid Emails Collected:")
print(valid_emails)
