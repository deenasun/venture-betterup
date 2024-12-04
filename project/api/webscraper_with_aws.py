import pandas as pd
from datetime import datetime
import boto3
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# AWS S3 setup
BUCKET_NAME = "BetterUp"
CSV_FILE_NAME = "courses_data.csv"

# AWS credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY'
)

# Load existing CSV data from S3
def load_existing_data_from_s3():
    try:
        s3_client.download_file(BUCKET_NAME, CSV_FILE_NAME, CSV_FILE_NAME)
        existing_df = pd.read_csv(CSV_FILE_NAME)
        logging.info("Existing CSV file loaded successfully from S3.")
    except Exception as e:
        logging.warning(f"No existing CSV file found in S3. Starting fresh: {e}")
        columns = ["Title", "Type", "Creation Date", "Days Since Creation",
                   "Training Materials", "Enrollments", "Completed"]
        existing_df = pd.DataFrame(columns=columns)
    return existing_df

# Save updated CSV to S3
def upload_updated_csv_to_s3(dataframe):
    try:
        local_file_path = f"./{CSV_FILE_NAME}"
        dataframe.to_csv(local_file_path, index=False)
        s3_client.upload_file(local_file_path, BUCKET_NAME, CSV_FILE_NAME)
        logging.info(f"CSV file updated and uploaded to S3 bucket '{BUCKET_NAME}'.")
        os.remove(local_file_path)  # Clean up local file after upload
    except Exception as e:
        logging.error(f"Failed to upload CSV to S3: {e}")

# Update the CSV file with new and historical data
def update_csv_with_historical_data(all_courses, existing_df):
    today = datetime.now().strftime("%Y-%m-%d")
    for course in all_courses:
        title = course["Title"]
        if title in existing_df["Title"].values:
            # Update existing course data
            idx = existing_df.index[existing_df["Title"] == title][0]
            existing_df.at[idx, "Enrollments"] = update_historical_field(
                existing_df.at[idx, "Enrollments"], course["Enrollments"], today)
            existing_df.at[idx, "Completed"] = update_historical_field(
                existing_df.at[idx, "Completed"], course["Completed"], today)
        else:
            # Add new course data
            new_row = {
                "Title": course["Title"],
                "Type": course["Type"],
                "Creation Date": course["Creation Date"],
                "Days Since Creation": course["Days Since Creation"],
                "Training Materials": course["Training Materials"],
                "Enrollments": {today: course["Enrollments"]},
                "Completed": {today: course["Completed"]},
            }
            existing_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)

    upload_updated_csv_to_s3(existing_df)

def update_historical_field(field, new_value, today):
    if isinstance(field, str):
        historical_data = eval(field)
    else:
        historical_data = {}
    historical_data[today] = new_value
    return historical_data

# Web scraping logic for courses
def scrape():
    # Set up Selenium WebDriver
    driver = webdriver.Chrome()
    try:
        # Navigate to the LMS login page
        driver.get("https://betterup.docebosaas.com/course/manage")
        
        # Login to the LMS
        login_to_lms(driver, "your_email@example.com", "your_password")

        # Wait for the course management page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # Scrape course data
        all_courses = scrape_courses(driver)
    finally:
        driver.quit()
    return all_courses

def login_to_lms(driver, username, password):
    try:
        # Enter username
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_email"))
        )
        username_field.send_keys(username)
        logging.info("Username entered successfully.")

        # Click the continue button
        continue_button = driver.find_element(By.CLASS_NAME, "button-primary")
        continue_button.click()

        # Enter password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_password"))
        )
        password_field.send_keys(password)
        logging.info("Password entered successfully.")

        # Submit the login form
        login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Log in']")
        login_button.click()
        logging.info("Login successful!")
    except Exception as e:
        logging.error(f"Error during login: {e}")

def scrape_courses(driver):
    courses = []
    try:
        # Find the course table
        tables = driver.find_elements(By.TAG_NAME, "table")
        course_table = tables[1]

        # Iterate through rows
        rows = course_table.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:  # Skip the header row
            cols = row.find_elements(By.TAG_NAME, "td")
            course = {
                "Title": cols[1].text,
                "Type": cols[2].text,
                "Creation Date": cols[3].text,
                "Days Since Creation": cols[4].text,
                "Training Materials": cols[5].text,
                "Enrollments": int(cols[6].text) if cols[6].text.isdigit() else 0,
                "Completed": int(cols[7].text) if cols[7].text.isdigit() else 0,
            }
            courses.append(course)
    except Exception as e:
        logging.error(f"Error scraping courses: {e}")
    return courses

def main():
    logging.info("Starting the BetterUp LMS scraper...")
    
    # Load existing data from S3
    existing_df = load_existing_data_from_s3()

    # Scrape current data from the LMS
    all_courses = scrape()

    # Update CSV with historical data
    update_csv_with_historical_data(all_courses, existing_df)

    logging.info("Scraper completed successfully.")

if __name__ == "__main__":
    main()
