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

    def select_language_tab(self, code_container, language="Python"):
        """
        Select a specific language tab (e.g., Python, Java).

        :param language: The language tab to select.
        """
        language_tabs = code_container.find_elements(
            By.CSS_SELECTOR,
            "div.font-menlo.relative.flex.h-10.cursor-pointer.items-center.justify-center",
        )

        for tab in language_tabs:
            if language in tab.text:
                tab.click()
                break

    def extract_code_type_bg3(self):
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

        self.select_language_tab(code_container, language="Python")

        code_section = code_container.find_element(
            By.CSS_SELECTOR, "code.language-python"
        )
        return code_section.get_attribute("innerText")

    def extract_code_type_fontMenlo(self):
        code_container = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "code.language-ruby",
                )
            )
        )

        return code_container.get_attribute("innerText")

    def close(self):
        """
        Close the browser and quit the WebDriver.
        """
        self.driver.quit()

    def run_scrapper(self, url, link):
        try:
            # Open the problem page
            scraper.open_page(url)

            solution_links = scraper.get_solution_links()

            print("Solution Links:", solution_links)

            # Navigate to a specific solution (e.g., the third link)
            scraper.navigate_to_solution(solution_links[link])

            try:
                # Extract the code using 'extract_code_type_bg3'
                code = scraper.extract_code_type_bg3()
            except Exception as e1:
                print(f"Failed to extract using `extract_code_type_bg3`. Error: {e1}")
                print("Attempting to extract using `extract_code_type_fontMenlo`...")

                try:
                    # Fallback to 'extract_code_type_fontMenlo'
                    code = scraper.extract_code_type_fontMenlo()
                except Exception as e2:
                    print(
                        f"Failed to extract using `extract_code_type_fontMenlo`. Error: {e2}"
                    )
                    print("No code extracted.")
                    raise

            code = scraper.extract_code_type_bg3()
            print("Extracted Code:")
            print(code)

        finally:
            scraper.close()


if __name__ == "__main__":
    load_dotenv()

    # Specify the path to your installed ChromeDriver
    chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

    # Initialize the LeetCodeScraper
    scraper = LeetCodeScraper(driver_path=chrome_driver_path, wait_time=10)

    url = "https://leetcode.com/problems/two-sum/solutions/"
    link_index = 1
    scraper.run_scrapper(url, link_index)
