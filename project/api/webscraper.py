from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import pandas as pd
import time
from bs4 import BeautifulSoup
import re

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

    # Login Button    
    login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Log in']")
    driver.execute_script("arguments[0].click();", login_button)
    print("Login successful!")

def scrape():
    WebDriverWait(driver, 10).until(
        EC.url_contains("/course/manage")  # Update with the post-login dashboard URL path
    )

    tables = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
    )
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
            df = pd.DataFrame(all_courses)
            df.to_csv("courses_data.csv", index=False)

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
        driver2.get(full_url)
        
        #Go into iframe
        WebDriverWait(driver2, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, 'legacy-wrapper-iframe'))
        )

        # Extract Numerical Stats
        try:
            counters = WebDriverWait(driver2, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "span12.player-stats-counter"))
            )
            stats = {
                "Enrollments": counters[0].text if len(counters) > 0 else None,
                "Days Since Launch": counters[1].text if len(counters) > 1 else None,
                "Training Materials": counters[2].text if len(counters) > 2 else None,
                "Not Started": counters[3].text if len(counters) > 3 else None,
                "In Progress": counters[4].text if len(counters) > 4 else None,
                "Completed": counters[5].text if len(counters) > 5 else None,
            }
            print(f"Numerical Stats for course {data_id}: {stats}")
            course_stats.append(stats)
        except Exception as e:
            print("An error occurred:", str(e))


       #Extract the post-course survey data
        try:
            report_navs = WebDriverWait(driver2, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'report-nav-btn'))
            )

            training_material_button = report_navs[1]
            try:
                driver2.execute_script("arguments[0].click();", training_material_button)
                print("Clicked training materials")

                #POST COURSE SURVEY DATA HERE
                try:
                    post_course_survey_element = WebDriverWait(driver2, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "reports-fancybox.fancybox\.ajax.report-grid-link"))
                    )
                    post_course_survey_href = post_course_survey_element.get_attribute('href')
                    driver2.get(post_course_survey_href)
                    print("Navigated to post-course survey")

                    # 1. Get Attendance:
                    attendance_element = driver2.find_element(By.CLASS_NAME, "poll-participants-count")
                    attendance_text = attendance_element.text
                    attendance = int(attendance_text.split(":")[-1].strip())

                    # 2. Get Likert Values:
                    likert_values = {}
                    likert_elements = driver2.find_elements(By.CLASS_NAME, "scaleCheckBox")
                    for i, element in enumerate(likert_elements):
                        likert_values[i] = element.text

                    # 3. Get "Like Most" Answers:
                    like_most_container = driver2.find_element(By.CSS_SELECTOR, "#poll-question-222")
                    like_most_answers = like_most_container.find_elements(By.CSS_SELECTOR, "div.poll-text-answer")
                    like_most_list = [answer.text.strip() for answer in like_most_answers]

                    # 4. Get "Improve" Answers:
                    improve_container = driver2.find_element(By.CSS_SELECTOR, "#poll-question-168")
                    improve_answers = improve_container.find_elements(By.CSS_SELECTOR, "div.poll-text-answer")
                    improve_list = [answer.text.strip() for answer in improve_answers]

                    post_course_survey = {
                        "Attendance": attendance,
                        "Likert": likert_values,
                        "Like Most": like_most_list,
                        "Improve": improve_list
                    }
                    print(post_course_survey)

                    driver2.back()
                except NoSuchElementException:
                    print("Element post-course not found")
                except Exception as e:
                    print("No post-course survey found because of error:", e)
                    post_course_survey = None

            except Exception as e:
                print("ERROR WITH TESTING:", e)

        except Exception as e:
            print("No navs :(:", str(e))

        

    driver2.quit()

    courses = []
    i = 0
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        enrollment_count = row.find_element(By.CLASS_NAME, "counter")
        course_data = {
            "Code": cols[1].text,
            "Type": cols[4].text,
            "Title": cols[3].text,
            "Creation Date": cols[5].text,
            "Days Since Creation": course_stats[i]["Days Since Launch"],
            "Enrollments": course_stats[i]["Enrollments"],
            "Not Started": course_stats[i]["Not Started"],
            "Stuck": course_stats[i]["In Progress"],
            "Completed": course_stats[i]["Completed"],
            "Post Course Survey": post_course_survey
        }
        courses.append(course_data)
        i += 1

    print("Filled Out Courses:", courses)
    return courses

# List to store all course data

# Wait for the email field to be present and then login
login("denysechan@berkeley.edu", "VSSBerkeley2024", driver)


# Scrape the entire page and store in all_courses
all_courses = []
scrape()

# # Save the data to a CSV file
df = pd.DataFrame(all_courses)
df.to_csv("courses_data.csv", index=False)

print("Data scraping completed. Saved to courses_data.csv")
