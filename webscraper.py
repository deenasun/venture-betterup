from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time

# Set up the WebDriver
driver = webdriver.Chrome()  

# Open the LMS login page
driver.get("https://betterup.docebosaas.com/course/manage")

# Function to log in to the LMS
def login(username, password):
    try:
        # Wait for the email field to be present and then click continue
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "form-control string email required")) 
            )
            username_field.send_keys(username)
            print("Email entered successfully.")
        except Exception as e:
            print(f"Failed to enter email: {e}")
        continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "button-primary"))
        )
        continue_button.click()

        # Password type and click
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        password_field.send_keys(password)
        login_button.click()

        # Wait for the login to complete (adjust condition if necessary)
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")  # Update with the post-login dashboard URL path
        )
        print("Login successful!")
    except TimeoutException:
        print("Login failed. Check your credentials or the page structure.")

# Function to collect course data from the current page
def scrape_current_page():
    courses = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tr")  # Adjust selector if necessary
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) > 0:
            course_data = {
                "Code": cols[0].text,
                "Title": cols[1].text,
                "Type": cols[2].text,
                "Creation Date": cols[3].text,
                "Sessions": cols[4].text,
                "Enrollments": cols[7].text
            }
            courses.append(course_data)
    return courses



# Call the login function with your credentials
login("denysechan@berkeley.edu", "VSSBerkeley2024")

# List to store all course data
all_courses = []

# Loop through all the pages using the pagination controls
while True:
    # Scrape the current page's courses
    all_courses.extend(scrape_current_page())

    try:
        # Find the "Next" button and click it
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
        )
        next_button.click()
        time.sleep(2)  # Wait for the page to load


    except TimeoutException:
        print("No more pages found.")
        break

# Close the driver
driver.quit()

# Save the data to a CSV file
df = pd.DataFrame(all_courses)
df.to_csv("courses_data.csv", index=False)

print("Data scraping completed. Saved to courses_data.csv")
