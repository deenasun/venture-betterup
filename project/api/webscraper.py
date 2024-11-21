from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from selenium.common.exceptions import StaleElementReferenceException

# Set up the WebDriver
driver = webdriver.Chrome()  

# Open the LMS login_and_scrape page
driver.get("https://betterup.docebosaas.com/course/manage")

# Function to log in to the LMS
def login_and_scrape(username, password):
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
    all_courses.extend(scrape_current_page(rows))

    pagination_table = tables[-1]
    pagination_controls = pagination_table.find_element(By.CLASS_NAME, "paginationControls")

    max_attempts = 50  # Maximum number of attempts to click the next button, prevents infinite loops
    attempts = 0

    while attempts < max_attempts:
        try:
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            tables = driver.find_elements(By.TAG_NAME, "table")
            course_table = tables[1]
            rows = course_table.find_elements(By.TAG_NAME, "tr")
            # Scrape the data from the current page
            curr_rows = course_table.find_elements(By.TAG_NAME, "tr")
            all_courses.extend(scrape_current_page(curr_rows))
            
            pagination_table = tables[-1]
            pagination_controls = pagination_table.find_element(By.CLASS_NAME, "paginationControls")
            div_for_next_button = pagination_controls.find_elements(By.TAG_NAME, 'div')[-1]
            next_button = div_for_next_button.find_element(By.TAG_NAME, 'a')
            
            if 'disabled' in next_button.get_attribute('class'):
                break  # Exit the loop if the next button is disabled
            try:
                driver.execute_script("arguments[0].click();", next_button)
            except Exception as error:
            # Dismiss the GDPR policy banner
                try:
                    banner = driver.find_element(By.CSS_SELECTOR, "gdpr-policy-banner")
                    dismiss_button = banner.find_element(By.CSS_SELECTOR, "button")
                    dismiss_button.click()
                except Exception as e:
                    print(f"Error dismissing banner: {e}")
                    pass  # Ignore the exception if the banner is not present
            
            print('clicked next')
            attempts += 1
        except StaleElementReferenceException:
            print('StaleElementReferenceException, retrying while attempts < max attempts')
            attempts += 1
        except Exception as e:
            print(f"Error: {e}")
            attempts += 1

    print('Reached end of all pages')
    # Close the browser
    driver.quit()
    return

# Function to collect course data from the current page
def scrape_current_page(rows):
    courses = []
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
        courses.append(course_data)
    return courses

# List to store all course data
all_courses = []

# Call login function with credentials
login_and_scrape("denysechan@berkeley.edu", "VSSBerkeley2024")


# # Save the data to a CSV file
df = pd.DataFrame(all_courses)
df.to_csv("courses_data.csv", index=False)

print("Data scraping completed. Saved to courses_data.csv")
