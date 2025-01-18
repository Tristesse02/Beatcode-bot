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

    def extract_code_type_fontMenlo_all(self, limit=10):
        """
        Extract code from elements where the class starts with 'language-' (e.g., language-ruby, language-sql).

        :param limit: The maximum number of code blocks to process. Default is 3.
        :return: A list of code contents that are Python; otherwise, return an empty list.
        """
        try:
            # Locate all elements with a class starting with 'language-'
            code_elements = self.wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "code[class^='language-']",  # Match any class that starts with 'language-'
                    )
                )
            )

            # Restrict to the first `limit` elements
            limited_code_elements = code_elements[:limit]

            extracted_codes = []
            for code_element in limited_code_elements:
                code = code_element.get_attribute("innerText")

                # Perform a quick check to validate if the code is Python
                print("Extracted code:", code)
                if self.is_python_code(code):
                    extracted_codes.append(code)
                else:
                    print("Extracted code is not Python. Skipping...")

            return extracted_codes
        except Exception as e:
            print(f"Failed to extract code. Error: {e}")
            return ""  # Return an empty list on any exception

    def filter_by_language(self, language="Python"):
        try:
            # Locate and click the widen button if it exists
            try:
                widen_button = self.wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "div.mt-\\[3px\\].cursor-pointer.text-\\[0px\\]",  # CSS selector for the widen button
                        )
                    )
                )
                print("Widen button found. Clicking to expand tags...")
                widen_button.click()
                time.sleep(1)  # Allow time for the tags to expand
            except Exception as e:
                print("Widen button not found or unable to click. Continuing...")

            # Locate the parent container of the language tags
            parent_container = self.driver.find_element(
                By.CSS_SELECTOR,
                "div.flex.w-full.items-start.gap-2.pr-6",
            )

            print("found parent container", parent_container)

            language_tags = parent_container.find_elements(
                By.CSS_SELECTOR, "span.inline-flex.cursor-pointer.items-center"
            )

            print("found language tags", language_tags)

            for tag in language_tags:
                if language in tag.text:
                    tag.click()
                    time.sleep(1)
                    return

        except Exception as e:
            print(f"Failed to extract using filter_by_language. Error: {e}")

    def close(self):
        """
        Close the browser and quit the WebDriver.
        """
        self.driver.quit()

    def run_scrapper(self, url, link, extract_code_type1, extract_code_type2):
        """
        Run the complete scraper process.

        :param url: The URL of the problem's solution page.
        :param link_index: The index of the solution link to scrape.
        """

        # Assign defaults if not provided
        if extract_code_type1 is None:
            extract_code_type1 = self.extract_code_type_bg3
        if extract_code_type2 is None:
            extract_code_type2 = self.extract_code_type_fontMenlo
        try:
            # Open the problem page
            self.open_page(f"{url}solutions/")

            self.filter_by_language("Python")
            solution_links = self.get_solution_links()

            print("Solution Links:", solution_links)

            # Navigate to a specific solution (e.g., the third link)
            self.navigate_to_solution(solution_links[link])

            try:
                # Extract the code using 'extract_code_type_bg3'
                code = extract_code_type1()
            except Exception as e1:
                print(f"Failed to extract using `extract_code_type_bg3`. Error: {e1}")
                print("Attempting to extract using `extract_code_type_fontMenlo`...")

                try:
                    # Fallback to 'extract_code_type_fontMenlo'
                    code = extract_code_type2()
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

    def validate_python_code(self):
        """
        Validate the extracted code to ensure it's written in Python.
        """
        data = self.load_json_file("solutions.json")
        combined_data = self.load_json_file("combined.json")
        processed_combined_data = {}

        for obj in combined_data:
            processed_combined_data[obj["title"]] = obj["source"]

        for problem_name, solutions in data.items():
            valid_solution = []
            for solution in solutions["solutions"]:
                if solution["language"] == "Python" and self.is_python_code(
                    solution["code"]
                ):
                    print(f"Valid solution for {problem_name} with {solution['code']}.")
                    valid_solution.append(solution)  # keep valid solution
                else:
                    print(
                        f"Invalid solution for {problem_name} detected. Recrawling..."
                    )

                    # Recrawl the solution
                    code = ""
                    for trial in range(3):  # Try up to 3 times
                        code = self.run_scrapper(
                            processed_combined_data[problem_name], trial + 3
                        )
                        print("Code extracted:", code)

                        if self.is_python_code(code):  # If valid code is found
                            valid_solution.append({"language": "Python", "code": code})
                            print(f"Valid Python code found for {problem_name}.")
                            break  # Stop trying once valid code is found

                    if not self.is_python_code(code):  # If no valid code after 3 trials
                        print(
                            f"Failed to find valid Python code for {problem_name} after 3 trials."
                        )
            # Replace the solutions with the validated solutions
            data[problem_name]["solutions"] = valid_solution

        with open("solutions.json", "w") as file:
            json.dump(data, file, indent=4)
            print("Validation complete.")

    def list_problems_less_than_2_solutions(self):
        """
        List problems that have less than 2 solutions and add more solutions if needed.
        """
        data = self.load_json_file("solutions.json")

        for problem_name, solutions in data.items():
            if len(solutions["solutions"]) < 2:
                for i in range(0, 3):
                    code = self.run_scrapper(
                        data[problem_name]["source"],
                        i,
                        self.extract_code_type_bg3,
                        self.extract_code_type_fontMenlo_all,
                    )
                    self.save_solution_to_file(
                        "solutions.json", problem_name, "Python", code
                    )

                    # Reload the updated data to check the number of solutions again
                    data = self.load_json_file("solutions.json")

                    # Check if the problem now has at least 2 solutions
                    if len(data[problem_name]["solutions"]) >= 2:
                        print(f"Problem '{problem_name}' has enough solutions.")
                        break

    def attached_source_to_problem(self):
        """
        Attach the source URL to the problem in the JSON file.

        :param filename: The JSON file to read from.
        """
        data = self.load_json_file("solutions.json")
        combined_data = self.load_json_file("combined.json")
        processed_combined_data = {}

        for obj in combined_data:
            processed_combined_data[obj["title"]] = obj["source"]

        for problem_name in data.keys():
            data[problem_name]["source"] = processed_combined_data[problem_name]

        with open("solutions.json", "w") as file:
            json.dump(data, file, indent=4)
            print("Validation complete.")

    def is_python_code(self, code):
        """
        Naive way to check if extracted code is written in Python.
        TODO: Need a more robust way to validate the code language.

        Args:
            code (string): The code content to check.

        Returns:
            boolean: True if the code is written in Python; otherwise, False.
        """
        processed_code = code.strip()
        return "class Solution:" in processed_code


if __name__ == "__main__":
    load_dotenv()

    # Specify the path to your installed ChromeDriver
    chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

    # Initialize the LeetCodeScraper
    scraper = LeetCodeScraper(driver_path=chrome_driver_path, wait_time=10)

    # TODO: Testing purpose
    # TODO: Add missing parameters to run_scrapper()
    # url = "https://leetcode.com/problems/isomorphic-strings/"
    # link_index = 2
    # code = scraper.run_scrapper(
    #     url,
    #     link_index,
    #     scraper.extract_code_type_bg3,
    #     scraper.extract_code_type_fontMenlo_all,
    # )
    # scraper.save_solution_to_file(
    #     "solutions.json", "Isomorphic Strings", "Python", code
    # )

    # scraper.close()

    # # Load the JSON file
    # TODO: Add missing parameters to run_scrapper()
    ## Main run
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

    # Validate the extracted Python code
    # scraper.validate_python_code()

    # List problems with less than 2 solutions
    # scraper.list_problems_less_than_2_solutions()
    
    # TODO: Will have to code scrape on the go and dynamically update to solution.json
    # The above code serve the purpose of testing the scraper and the code extraction

    # Always close the connection!
    scraper.close()
