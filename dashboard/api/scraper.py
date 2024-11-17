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

try:
    username_field = WebDriverWait(driver, 25).until(
        EC.element_to_be_clickable((By.ID, "user_email")) 
    )
    print('username found', username_field)
except:
    print('element not found')