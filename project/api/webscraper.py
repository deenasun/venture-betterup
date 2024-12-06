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
        data_id = 668
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

        #Extract the post-course survey data
        try:
            report_navs = WebDriverWait(driver2, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'report-nav-btn'))
            )
            # print("Report Navs:", report_navs)

            training_material_button = report_navs[1]
            # print("Training Material Button:", training_material_button)
            try:
                # try:
                #     button2 = WebDriverWait(driver2, 10).until(
                #         EC.presence_of_element_located((By.CLASS_NAME, "bg-white.open.ng-star-inserted"))
                #     )
                #     button2.click()
                # except Exception as e:
                #     print(f"Error dismissing banner: {e}")
                #     pass  # Ignore the exception if the banner is not present

                driver2.execute_script("arguments[0].click();", training_material_button)
                print("Clicked training materials")
                time.sleep(5)

                try:
                    post_course_survey_element = WebDriverWait(driver2, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "reports-fancybox.fancybox\.ajax.report-grid-link"))
                    )
                    #print("Post-Course Survey Element:", post_course_survey_element)

                    post_course_survey_href = post_course_survey_element.get_attribute('href')
                    #print("Post-Course Survey href:", post_course_survey_href)

                    driver2.get(post_course_survey_href)
                    html = driver2.page_source
                    #print("HTML:", html)
                    soup = BeautifulSoup(html, 'html.parser')

                    all_text = soup.get_text()
                    print("All Text:\n", all_text)

                    # Process the text to remove everything above "Attendance"
                    filtered_text = all_text.split("Attendance:")[1]  # Split and keep only relevant part
                    filtered_text = "Attendance:" + filtered_text  # Re-add "Attendance:" for clarity

                    # Parse the filtered text
                    lines = filtered_text.splitlines()  # Split into lines for easier processing
                    lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines

                    # Initialize the dictionary to store parsed data
                    post_course_survey = {}

                    # Function to safely extract numbers with regex
                    def safe_extract_number(text, default=0):
                        match = re.search(r"\d+", text)
                        return int(match.group()) if match else default

                    # Extract "Attendance"
                    attendance_line = next((line for line in lines if line.startswith("Attendance:")), None)
                    post_course_survey["Attendance"] = safe_extract_number(attendance_line)

                    # Extract Likert scale data
                    likert_question_index = next((i for i, line in enumerate(lines) if "How likely are you to recommend" in line), None)
                    if likert_question_index is not None:
                        likert_scale_values = lines[likert_question_index + 2] if len(lines) > likert_question_index + 2 else ""
                        post_course_survey["Likert"] = {
                            # "0": safe_extract_number(likert_scale_values.split("0)")[1]),
                            # "1": safe_extract_number(likert_scale_values.split("1)")[1]),
                            # "2": safe_extract_number(likert_scale_values.split("2)")[1]),
                            # "3": safe_extract_number(likert_scale_values.split("3)")[1]),
                            # "4": safe_extract_number(likert_scale_values.split("4)")[1]),
                            # "5": safe_extract_number(likert_scale_values.split("5)")[1]),
                            # "6": safe_extract_number(likert_scale_values.split("6)")[1]),
                            # "7": safe_extract_number(likert_scale_values.split("7)")[1]),
                            # "8": safe_extract_number(likert_scale_values.split("8)")[1]),
                            # "9": safe_extract_number(likert_scale_values.split("9)")[1]),
                            # "10": safe_extract_number(likert_scale_values.split("10)")[1])
                        }

                    # Extract knowledge improvement data
                    knowledge_question_index = next((i for i, line in enumerate(lines) if "My knowledge improved" in line), None)
                    if knowledge_question_index is not None:
                        knowledge_data = lines[knowledge_question_index + 1]
                        pattern = r"(.+?)(\d+)"
                        result = {}
                        while match := re.search(pattern, knowledge_data):
                            key = match.group(1).strip()  # Text before the number (key)
                            value = int(match.group(2))   # The number (value)
                            result[key] = value           # Add to dictionary
                            
                            # Remove the processed part from the text
                            knowledge_data = knowledge_data[match.end():].strip()
                        post_course_survey["Knowledge"] = result

                    # Extract what users liked most
                    like_question_index = next((i for i, line in enumerate(lines) if "What did you like most" in line), None)
                    if like_question_index is not None:
                        like_answers = lines[like_question_index + 1:]  # Extract all text answers after the question
                        like_answers = [answer for answer in like_answers if not answer.startswith("4) ")]  # Stop at the next question
                        post_course_survey["Like"] = like_answers

                    # Extract improvement suggestions
                    improve_question_index = next((i for i, line in enumerate(lines) if "What can we do to improve" in line), None)
                    if improve_question_index is not None:
                        improve_answers = lines[improve_question_index + 1:]  # Extract all text answers for this question
                        post_course_survey["Improve"] = improve_answers

                    # Print the final dictionary
                    print(post_course_survey)

                    driver2.back()
                    print("Current URL:", driver2.current_url)
                except NoSuchElementException:
                    print("Element post-course found")
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
