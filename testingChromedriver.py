import os
import json
import time
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

    def load_json_file(self, filename):
        """
        Load data from a JSON file, returning an empty dictionary if the file does not exist or is empty.
        """
        if not os.path.exists(filename) or os.stat(filename).st_size == 0:
            return (
                {}
            )  # Return an empty dictionary if the file doesn't exist or is empty

        with open(filename, "r") as file:
            return json.load(file)  # Load the JSON content

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
                time.sleep(1)
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
        """
        Extract code from elements where the class starts with 'language-' (e.g., language-ruby, language-sql).

        :return: The code content as a string if it's Python; otherwise, return an empty string.
        """
        try:
            # Locate the element with a class starting with 'language-'
            code_container = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "code[class^='language-']",  # Match any class that starts with 'language-'
                    )
                )
            )
            code = code_container.get_attribute("innerText")

            # Perform a quick check to validate if the code is Python
            if self.is_python_code(code):
                return code
            else:
                print("Extracted code is not Python. Returning an empty string.")
                return ""  # Return an empty string instead of raising an exception
        except Exception as e:
            print(f"Failed to extract code. Error: {e}")
            return ""  # Return an empty string on any exception

    def filter_by_language(self, language="Python"):
        try:
            parent_container = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.flex.w-full.items-start.gap-2.pr-6.overflow-hidden",
                    )
                )
            )

            language_tags = parent_container.find_elements(
                By.CSS_SELECTOR, "span.inline-flex.cursor-pointer.items-center"
            )

            for tag in language_tags:
                if language in tag.text:
                    tag.click()
                    time.sleep(1)
                    return

        except Exception as e:
            print(f"Failed to extract using `filter_by_language`. Error: {e}")

    def close(self):
        """
        Close the browser and quit the WebDriver.
        """
        self.driver.quit()

    def run_scrapper(self, url, link):
        """
        Run the complete scraper process.

        :param url: The URL of the problem's solution page.
        :param link_index: The index of the solution link to scrape.
        """
        try:
            # Open the problem page
            scraper.open_page(f"{url}solutions/")

            scraper.filter_by_language("Python")
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
            
            print("Extracted Code:")
            print(code)
            return code

        except Exception as e:
            print(f"An error occurred: {e}")
            return ""

    def save_solution_to_file(self, filename, problem_name, language, code):
        """
        Save the problem name and solution to a JSON file.

        :param filename: The JSON file to write to.
        :param problem_name: Name of the problem.
        :param language: Language of the solution.
        :param code: The solution code.
        """
        data = self.load_json_file(filename)

        if problem_name in data:
            existing_solutions = data[problem_name]["solutions"]
            for solution in existing_solutions:
                if solution["language"] == language and solution["code"] == code:
                    print("Solution already exists, skipping.")
                    return
            # Add the new solution to the problem's solutions list
            data[problem_name]["solutions"].append({"language": language, "code": code})
        else:
            # Add a new problem with its solution
            data[problem_name] = {"solutions": [{"language": language, "code": code}]}

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Solution saved to {problem_name} in {language}.")

    def is_python_code(self, code):
        python_keywords = ["def", "import", "self", "class", "return", "lambda"]
        python_syntax = [":", "    "]

        if any(keyword in code for keyword in python_keywords) and any(
            syntax in code for syntax in python_syntax
        ):
            return True
        return False


if __name__ == "__main__":
    load_dotenv()

    # Specify the path to your installed ChromeDriver
    chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

    # Initialize the LeetCodeScraper
    scraper = LeetCodeScraper(driver_path=chrome_driver_path, wait_time=10)

    url = "https://leetcode.com/problems/longest-common-prefix/"
    link_index = 2
    code = scraper.run_scrapper(url, link_index)
    scraper.save_solution_to_file(
        "solutions.json", "Longest Common Prefix", "Python", code
    )

    scraper.close()

    # # Load the JSON file
    # try:
    #     with open("combined.json", "r") as f:
    #         data = json.load(f)
    # except FileNotFoundError:
    #     raise FileNotFoundError("File not found")

    # # print(len(data))
    # try:
    #     for problem in data:
    #         problem_name = problem["title"]
    #         problem_url = problem["source"]

    #         for idx in range(1, 3):
    #             code = scraper.run_scrapper(problem_url, idx)
    #             scraper.save_solution_to_file(
    #                 "solutions.json", problem_name, "Python", code
    #             )
    #             time.sleep(4)
    # finally:
    #     # Close the browser
    #     scraper.close()
