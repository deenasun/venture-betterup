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
    # Wait for the email field to be present and then click continue
    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "user_email")) 
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
    try:
        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "user_password"))
        )
        password_field.send_keys(password)
        print('Password entered successfully.')
    except Exception as e:
        print(f"Failed to enter password: {e}")
    login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Log in']")
    driver.execute_script("arguments[0].click();", login_button)

    # Wait for the login to complete (adjust condition if necessary)
    WebDriverWait(driver, 10).until(
        EC.url_contains("/course/manage")  # Update with the post-login dashboard URL path
    )
    print("Login successful!")
    tables = driver.find_elements(By.TAG_NAME, "table")
    course_table = tables[1]
    rows = course_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        course_data = {
            "Code": cols[0].text,
            "Title": cols[1].text,
            "Type": cols[2].text,
            "Creation Date": cols[3].text,
            "Sessions": cols[4].text,
            "Enrollments": cols[7].text
        }
        # print(course_data)
        all_courses.append(course_data)
    return

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

# List to store all course data
all_courses = []

# Call the login function with your credentials
login("denysechan@berkeley.edu", "VSSBerkeley2024")

print(all_courses)
# # Loop through all the pages using the pagination controls
# while True:
#     # Scrape the current page's courses
#     all_courses.extend(scrape_current_page())

#     try:
#         # Find the "Next" button and click it
#         next_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
#         )
#         next_button.click()
#         time.sleep(2)  # Wait for the page to load


#     except TimeoutException:
#         print("No more pages found.")
#         break

# # Close the driver
# driver.quit()

# # Save the data to a CSV file
# df = pd.DataFrame(all_courses)
# df.to_csv("courses_data.csv", index=False)

# print("Data scraping completed. Saved to courses_data.csv")
