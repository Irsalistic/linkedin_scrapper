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

load_dotenv()

# Initialize the driver with incognito mode
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def login_to_linkedin():
    """Log in to LinkedIn."""
    driver.get("https://www.linkedin.com/login")
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")

    username.send_keys(os.getenv("linkedin_email"))
    password.send_keys(os.getenv("linkedin_keys"))

    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(20)


def search_for_companies(query):
    """Search for companies based on the query."""
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search']"))
    )
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Companies']"))).click()
    time.sleep(3)


def extract_company_details():
    """Extract details for each company."""
    companies = driver.find_elements(By.CLASS_NAME, "entity-result__title-text")
    print(f"companies:{companies}")
    for index, company in enumerate(companies):
        try:
            company_link = company.find_element(By.TAG_NAME, "a")
            company_name = company_link.text
            company_link.click()
            print(f"Processing Company {index + 1}: {company_name}")

            # Wait for and click "About" section
            about_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/about/')]"))
            )
            about_link.click()

            # Scroll down and extract company info
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            company_info = driver.find_elements(By.XPATH, "//dd[contains(@class, 'mb4')]")
            for p in company_info:
                print(f"  Info: {p.text}")

            # Check "People" section
            people_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/people/')]"))
            )
            people_link.click()
            time.sleep(3)

            # Search for "Founder" or CEO
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@placeholder='Search employees by title, keyword or school']"))
            )
            search_box.send_keys("Founder")
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)

            ceo = driver.find_element(By.XPATH,
                                      "/html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[2]/div/div/div[2]/div/div[1]/ul/li[1]/div/section/div/div/div[2]/div[1]/a/div")
            print(f"  CEO/Founder: {ceo.text}")

            driver.back()  # Go back to company search results

        except Exception as e:
            print(f"Error processing company {index + 1}: {e}")
        finally:
            driver.back()
            time.sleep(3)


def main():
    """Main workflow."""
    login_to_linkedin()
    search_for_companies("ERP Solutions")
    extract_company_details()

    driver.quit()


if __name__ == "__main__":
    main()
