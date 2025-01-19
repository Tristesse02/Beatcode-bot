import os
import re
import time
import json
import random
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()


class BeatCodeAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """
        Set up the Selenium WebDriver with the specified ChromeDriver path.
        """
        chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")
        self.driver = webdriver.Chrome(service=Service(chrome_driver_path))
        self.wait = WebDriverWait(self.driver, 10)

    def teardown_driver(self):
        """
        Quit the Selenium WebDriver.
        """
        if self.driver:
            self.driver.quit()

    def handle_login(self, username, password):
        """Log in to the BeatCode website.

        Args:
            username str: just a valid email
            password str: and a valid password
        """
        try:
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            username_field.send_keys(username)
            password_field.send_keys(password)

            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )

            submit_button.click()

            print("Login process initiated")
        except Exception as e:
            print(f"Failed to log in. Error: {e}")

    def navigate_to_custom_page(self):
        """Navigate to the custom page on the BeatCode website."""
        try:
            custom_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/custom']"))
            )

            custom_button.click()
            print("Navigating to custom page")
        except Exception as e:
            print(f"Failed to navigate to custom page. Error: {e}")

    def navigate_to_lobby_page(self):
        try:
            lobby_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/custom/lobby']"))
            )

            lobby_button.click()
            print("Navigating to lobby page")
        except Exception as e:
            print(f"Failed to navigate to lobby page. Error: {e}")

    def click_join_room(self):
        """
        Check for the first room available and click on join room
        # TODO: Add robustness in checking for room availability
        """
        try:
            room_container = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.flex.items-center.justify-between.rounded-lg.border.border-secondary.p-4",
                    )
                )
            )
            print("Room container found.")

            join_button = room_container.find_element(
                By.CSS_SELECTOR,
                "a[href^='/room']",  # Find the <a> tag with href starting with '/room'
            )

            join_button.click()
            print("Clicked 'Join Room' button.")
        except Exception as e:
            print(f"Failed to locate or click the 'Join Room' button. Error: {e}")

    def click_join_room_laufey(self):
        """Check if the room with title 'Laufey' exists and click the 'Join Room' button.
        TODO: Just for testing purpose
        """
        try:
            room_containers = self.wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "div.flex.items-center.justify-between.rounded-lg.border.border-secondary.p-4",
                    )
                )
            )
            print("Room containers found.")

            for room_container in room_containers:
                try:
                    room_title = room_container.find_element(By.TAG_NAME, "h2")
                    if "Laufey" in room_title.text.strip():
                        print("Room with title 'Laufey' found.")
                        join_button = room_container.find_element(
                            By.CSS_SELECTOR, "a[href^='/room']"
                        )
                        join_button.click()
                        print("Clicked 'Join Room' button.")
                        return
                except Exception as e:
                    print(f"Error processing a room container: {e}")

            print("No room with title 'Laufey' found.")

        except Exception as e:
            print(f"Failed to locate room containers. Error: {e}")

    def click_next_button(self):
        """Click the 'Next' button to proceed to the game room."""
        try:
            next_button = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "button.ring-offset-background.focus-visible\\:ring-ring.inline-flex.items-center.justify-center.gap-2.whitespace-nowrap.rounded-md.px-8.mt-4.text-lg",
                    )
                )
            )
            next_button.click()
            print("Clicked the next button.")
        except Exception as e:
            print(f"Failed to locate or click the button. Error: {e}")

    def switch_to_new_window(self):
        """Switch to the new game window that opens after clicking the 'Next' button."""
        try:
            original_window = self.driver.current_window_handle
            print(f"Original window: {original_window}")

            WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)

            for window in self.driver.window_handles:
                if window != original_window:
                    self.driver.switch_to.window(window)
                    print(f"Switched to new window: {window}")
                    break
        except Exception as e:
            print(f"Failed to switch to the new window. Error: {e}")

    def check_if_on_game_room(self):
        """Check if the current URL is the game room URL."""
        try:
            self.switch_to_new_window()
            attempts = 0
            while (
                "https://www.beatcode.dev/game" not in self.driver.current_url
                and attempts < 5
            ):
                time.sleep(5)
                print("Waiting for game room to load...")
                attempts += 1

            if "https://www.beatcode.dev/game" in self.driver.current_url:
                print("Successfully navigated to the game room.")
            else:
                print("Game room did not load in time.")
        except Exception as e:
            print(f"Error while checking for game room. Error: {e}")

    def fetch_problem_solution(self, filename="solutions.json", useSolutionIdx=0):
        """Fetch the solution code for the current problem statement.

        Args:
            filename (str, optional): json file containing answer key. Defaults to "solutions.json".
            useSolutionIdx (int, optional): index to get the solution. Defaults to 0.

        Returns:
            _type_: the code to the problem statement

        TODO: Add the ability to fetch the solution on the go
        TODO: Add robustness for useSolutionIdx (various index should be accepted)
        """
        solutions = {}
        try:
            problem_statement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "h2.mb-2.text-2xl.font-semibold")
                )
            )

            problem_statement_text = problem_statement.text
            print(f"Problem statement: {problem_statement_text}")

            with open(filename, "r") as file:
                solutions = json.load(file)
            return solutions[problem_statement_text]["solutions"][useSolutionIdx][
                "code"
            ]

        except Exception as e:
            print(f"Failed to fetch the problem statement. Error: {e}")

    def input_code_into_editor(
        self,
        code,
        short_line_threshold=30,
        typing_speed_short=0.05,
        typing_speed_long=0.3,
        typo_chance=0.15,
    ):
        """
        Input the code into the editor on the game room page

        Args:
            code (str): the solution code that will be inputted into the editor
            short_line_threshold (int, optional): Define what to be short and what to be long line. Defaults to 30.
            typing_speed_short (float, optional): typing speed for short line. Defaults to 0.05.
            typing_speed_long (float, optional): typing speed for long line. Defaults to 0.5.
            typo_chance (float, optional): Chance to get a typo. Defaults to 0.15.
        """
        try:
            editor_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
            )
            print("Editor container located.")

            editor_container.click()
            time.sleep(1)

            editor_container.send_keys(Keys.CONTROL + "a")
            editor_container.send_keys(Keys.DELETE)

            lines = code.split("\n")
            for line in lines:
                typing_speed = (
                    typing_speed_short
                    if len(line.strip()) <= short_line_threshold
                    else typing_speed_long
                )

                editor_container.send_keys(Keys.CONTROL + Keys.BACKSPACE)

                for char in line:
                    if random.random() < typo_chance:
                        typo_char = random.choice("abcdefghijklmnopqrstuvwxyz")
                        editor_container.send_keys(typo_char)
                        time.sleep(typing_speed)
                        editor_container.send_keys(Keys.BACKSPACE)
                        time.sleep(typing_speed)

                    editor_container.send_keys(char)
                    time.sleep(random.uniform(typing_speed_short, typing_speed_long))

                editor_container.send_keys(Keys.SPACE)

                editor_container.send_keys(Keys.RETURN)

            print("Code successfully input into the editor.")
        except Exception as e:
            print(f"Failed to input code into the editor. Error: {e}")

    def read_and_highlight_problem(self, read_speed=0.1):
        """Read the problem statement and highlight the keywords."""
        try:
            problem_container = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.h-full.overflow-y-auto.bg-background.px-4.py-5 > div:nth-child(3)",
                    )
                )
            )
            print("Problem container located.")

            children = problem_container.find_elements(By.XPATH, "./*")

            for i, child in enumerate(children):
                print(f"Child {i + 1}:")
                print(f"Tag Name: {child.tag_name}")
                print(f"Inner HTML: {child.get_attribute('innerHTML')}")
                print(f"Text Content: {child.text.strip()}")
                print("-" * 50)

                innerHTML = child.get_attribute("innerHTML").split()
                for index, word in enumerate(innerHTML):
                    tmp = innerHTML.copy()
                    if "<" not in word and ">" not in word:
                        tmp[index] = self.native_string(word)
                    else:
                        tmp[index] = self.native_html(word)

                    highlighted_html = " ".join(tmp)
                    self.driver.execute_script(
                        "arguments[0].innerHTML = arguments[1];",
                        child,
                        highlighted_html,
                    )
                    time.sleep(read_speed)

                highlighted_html = " ".join(innerHTML)
                self.driver.execute_script(
                    "arguments[0].innerHTML = arguments[1];", child, highlighted_html
                )

            print("Finished reading the problem statement.")
        except Exception as e:
            print(f"Failed to read and highlight the problem statement. Error: {e}")

    def native_html(self, word):
        """Highlight the word in the HTML format

        Args:
            word (str): the word that contains HTML tags

        Returns:
            _type_: the highlighted word in HTML format
        """
        idx = word.find(">")
        return word[:idx] + f" style='background-color: #1e8758;' " + word[idx:]

    def native_string(self, word):
        """Highlight the word in the string format"""
        return f"<span style='background-color: #1e8758;'>{word}</span>"

    def click_submit_program(self):
        """
        Click the submit button to complete the program submission.
        """
        try:
            # Locate the button using a combination of class names
            submit_button = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "button.ring-offset-background.focus-visible\\:ring-ring.inline-flex.justify-center.gap-2",
                    )
                )
            )
            # Click the button
            submit_button.click()
            print("Clicked the submit button.")
        except Exception as e:
            print(f"Failed to locate or click the submit button. Error: {e}")

    def click_next_question(self):
        try:
            submit_button = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "button.ring-offset-background.focus-visible\\:ring-ring.inline-flex.justify-center.h-10",
                    )
                )
            )
            submit_button.click()
        except Exception as e:
            print(f"Failed to locate or click the next question button. Error: {e}")


# Example usage:
if __name__ == "__main__":
    automation = BeatCodeAutomation()
    automation.setup_driver()

    try:
        automation.driver.get("https://www.beatcode.dev/home")
        if automation.driver.current_url == "https://www.beatcode.dev/home":
            print("You are on the home page")
        elif automation.driver.current_url == "https://www.beatcode.dev/login":
            automation.handle_login("kobop54654@halbov.com", "123456789")
            time.sleep(2)
            automation.navigate_to_custom_page()
            time.sleep(1)
            automation.navigate_to_lobby_page()
            time.sleep(1)
            automation.click_join_room_laufey()
            time.sleep(1)
            automation.click_next_button()
            time.sleep(5)
            automation.check_if_on_game_room()
            time.sleep(2)

            automation.read_and_highlight_problem()

            code = automation.fetch_problem_solution("solutions.json", 0)

            # TODO: If fail, we will have to fetch solution on the go!
            automation.input_code_into_editor(code)
            time.sleep(1)
            automation.click_submit_program()
            time.sleep(2)
            automation.click_next_question()
            time.sleep(15)
    finally:
        automation.teardown_driver()
