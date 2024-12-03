from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import time

# Set up the WebDriver
driver = webdriver.Chrome()  

# Open the LMS login_and_scrape page
driver.get("https://betterup.docebosaas.com/course/manage")

# Function to log in to the LMS
def login(username, password, driver):
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
    print("Login successful!")

def scrape():
    # Wait for the email field to be present and then click continue
    login("denysechan@berkeley.edu", "VSSBerkeley2024", driver)
    # #Login Done!
    
    WebDriverWait(driver, 10).until(
        EC.url_contains("/course/manage")  # Update with the post-login dashboard URL path
    )
    tables = driver.find_elements(By.TAG_NAME, "table")
    course_table = tables[1]
    rows = course_table.find_elements(By.TAG_NAME, "tr")
    all_courses.extend(scrape_current_page(rows, []))

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

            # Extract 'data-id' values
            data_ids = []
            for row in rows:
                data_id = row.get_attribute("data-id")
                if data_id:  # Only append non-empty data-id values
                    data_ids.append(data_id)

            # Scrape the data from the current page
            curr_rows = course_table.find_elements(By.TAG_NAME, "tr")
            all_courses.extend(scrape_current_page(curr_rows, data_ids))

            rows = driver.find_elements(By.CSS_SELECTOR, "tr[_ngcontent-ng-c3445667421]")
            
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
def scrape_current_page(rows, data_ids):
    base_url = "https://betterup.docebosaas.com/course/edit/"
    course_stats = []
    driver2 = webdriver.Chrome()
    driver2.get("https://betterup.docebosaas.com/course/manage")
    login("denysechan@berkeley.edu", "VSSBerkeley2024", driver2)
    for data_id in data_ids:
        full_url = f"{base_url}{data_id};tab=reports"
        print(f"Navigating to: {full_url}")
    
        # Navigate to the URL
        driver2.get(full_url)
        # time.sleep(5)  # Adjust the sleep time as needed or use explicit waits
        
        WebDriverWait(driver2, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, 'legacy-wrapper-iframe'))
        )

        # Extract "To Begin," "In Progress," and "Completed" numbers dynamically
        try:
            counters = WebDriverWait(driver2, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "span12.player-stats-counter"))
            )
            #Extract and map the values
            stats = {
                "Enrollments": counters[0].text if len(counters) > 0 else None,
                "Days Since Launch": counters[1].text if len(counters) > 1 else None,
                "Training Materials": counters[2].text if len(counters) > 2 else None,
                "Not Started": counters[3].text if len(counters) > 3 else None,
                "In Progress": counters[4].text if len(counters) > 4 else None,
                "Completed": counters[5].text if len(counters) > 5 else None,
            }
            print(f"Data for course {data_id}: {stats}")
            course_stats.append(stats)
        except TimeoutException:
            print("Timed out waiting for the element to load")
        except NoSuchElementException:
            print("Element not found")
        except Exception as e:
            print("An error occurred:", str(e))

    driver2.quit()

    courses = []
    i = 0
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        enrollment_count = row.find_element(By.CLASS_NAME, "counter")
        course_data = {
            #"Code": cols[0].text,
            "Title": cols[1].text,
            "Type": cols[2].text,
            "Creation Date": cols[3].text,
            "Days Since Creation": course_stats[i]["Days Since Launch"],
            "Training Materials": course_stats[i]["Training Materials"],
            "Sessions": cols[4].text,
            "Enrollments": enrollment_count.text if enrollment_count else 0,
            "Not Started": course_stats[i]["Not Started"],
            "Stuck": course_stats[i]["In Progress"],
            "Completed": course_stats[i]["Completed"]
        }
        courses.append(course_data)
        i += 1

    print("Filled Out Courses": courses)
    return courses

# List to store all course data
all_courses = []

# Call login function with credentials
scrape()


# # Save the data to a CSV file
df = pd.DataFrame(all_courses)
df.to_csv("courses_data.csv", index=False)

print("Data scraping completed. Saved to courses_data.csv")
