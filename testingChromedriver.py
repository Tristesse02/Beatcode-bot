import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

## TODO: Make this a dynamic function - a better idea is to turn this thing into a class
# Specify the path to your installed ChromeDriver
chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

# Set up Selenium WebDriver with the specified ChromeDriver path
driver = webdriver.Chrome(service=Service(chrome_driver_path))

driver.get("https://leetcode.com/problems/two-sum/solutions/")

# Start fixing here:

# Wait until webpage fully loaded:
wait = WebDriverWait(driver, 10)  # Wait up to 20 seconds

link_elements = wait.until(
    EC.presence_of_all_elements_located(
        (
            By.CSS_SELECTOR,
            "a.no-underline.hover\\:text-blue-s.dark\\:hover\\:text-dark-blue-s.truncate.w-full",
        )
    )
)

# print("Text:", link_elements[1].get_attribute("href"))  # Get the visible text
link = link_elements[3].get_attribute(
    "href"
)  # Get the visible text # TODO: the link_element value represent what link we want to click on. Can be change dynamically
driver.get(link)  # We can get one or multiple answer for the  problem

code_container = wait.until(
    EC.presence_of_element_located(
        (
            By.CSS_SELECTOR,
            "div.border-gray-3.dark\\:border-dark-gray-3.mb-6.overflow-hidden.rounded-lg.border.text-sm",
        )
    )
)

# Find all the tabs inside the parent container
language_tabs = code_container.find_elements(
    By.CSS_SELECTOR,
    "div.font-menlo.relative.flex.h-10.cursor-pointer.items-center.justify-center",
)

# Iterate over the tabs and click the one containing 'Python'
for tab in language_tabs:
    print("Tab Text:", tab.text)  # Debugging: Print the text of each tab
    if "Python" in tab.text:  # Match Python or Python3
        print(f"Clicking on tab: {tab.text}")
        tab.click()
        break

# print(code_container.get_attribute("innerText"))
code_section = code_container.find_element(By.CSS_SELECTOR, "code.language-python")

# print(code_container.get_attribute("innerText"))
print(code_section.get_attribute("innerText"))


driver.quit()
