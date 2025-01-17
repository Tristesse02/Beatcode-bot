import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

load_dotenv()

# Specify the path to your installed ChromeDriver
chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

# Set up Selenium WebDriver with the specified ChromeDriver path
driver = webdriver.Chrome(service=Service(chrome_driver_path))

