import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LeetCodeScraper:
    def __init__(self, driver_path, wait_time=10):
        """
        Initialize the LeetCodeScraper with WebDriver.

        :param driver_path: Path to the ChromeDriver.
        :param wait_time: Maximum wait time for elements to load.
        """
        self.driver = webdriver.Chrome(service=Service(driver_path))
        self.wait = WebDriverWait(self.driver, wait_time)

    def open_page(self, url):
        """
        Open a specified URL in the browser.

        :param url: The URL to navigate to.
        """
        self.driver.get(url)

    def get_solution_links(self):
        """
        Retrieve solution links from the problem's page.

        :return: A list of solution links.
        """
        link_elements = self.wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "a.no-underline.hover\\:text-blue-s.dark\\:hover\\:text-dark-blue-s.truncate.w-full",
                )
            )
        )
        return [link.get_attribute("href") for link in link_elements]

    def navigate_to_solution(self, link):
        """
        Navigate to a specific solution link.

        :param link: The solution link to open.
        """
        self.driver.get(link)

    def select_language_tab(self, language="Python"):
        """
        Select a specific language tab (e.g., Python, Java).

        :param language: The language tab to select.
        """
        code_container = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.border-gray-3.dark\\:border-dark-gray-3.mb-6.overflow-hidden.rounded-lg.border.text-sm",
                )
            )
        )

        language_tabs = code_container.find_elements(
            By.CSS_SELECTOR,
            "div.font-menlo.relative.flex.h-10.cursor-pointer.items-center.justify-center",
        )

        for tab in language_tabs:
            if language in tab.text:
                tab.click()
                break

    def extract_code(self):
        """
        Extract the code content from the selected tab.

        :return: The code content as a string.
        """
        code_container = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.border-gray-3.dark\\:border-dark-gray-3.mb-6.overflow-hidden.rounded-lg.border.text-sm",
                )
            )
        )
        code_section = code_container.find_element(
            By.CSS_SELECTOR, "code.language-python"
        )
        return code_section.get_attribute("innerText")

    def close(self):
        """
        Close the browser and quit the WebDriver.
        """
        self.driver.quit()


if __name__ == "__main__":
    load_dotenv()

    # Load environment variables
    chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

    # Initialize the scraper
    scraper = LeetCodeScraper(driver_path=chrome_driver_path, wait_time=10)

    try:
        # Open the problem page
        scraper.open_page("https://leetcode.com/problems/two-sum/solutions/")

        # Get solution links
        solution_links = scraper.get_solution_links()
        print("Solution Links:", solution_links)

        # Navigate to a specific solution (e.g., the third link)
        scraper.navigate_to_solution(solution_links[3])

        # Select the Python tab
        scraper.select_language_tab(language="Python")

        # Extract and print the code
        code = scraper.extract_code()
        print("Extracted Code:")
        print(code)

    finally:
        # Close the scraper
        scraper.close()
