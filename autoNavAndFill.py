import os
import time
import random
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()


def handle_login(username, password):
    try:
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = wait.until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        username_field.send_keys(username)
        password_field.send_keys(password)

        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )

        submit_button.click()

        print("Login proceess initiated")
    except Exception as e:
        print(f"Failed to log in. Error: {e}")


def naviate_to_custom_page():
    try:
        custom_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/custom']"))
        )

        custom_button.click()
        print("Navigating to custom page")
    except Exception as e:
        print(f"Failed to navigate to custom page. Error: {e}")


def naviate_to_lobby_page():
    try:
        custom_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/custom/lobby']"))
        )

        custom_button.click()
        print("Navigating to lobby page")
    except Exception as e:
        print(f"Failed to navigate to custom page. Error: {e}")


def click_join_room():
    """
    Check if the 'Join Room' button exists and click it.
    """
    try:
        # Locate the parent container of the room
        room_container = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.flex.items-center.justify-between.rounded-lg.border.border-secondary.p-4",
                )
            )
        )
        print("Room container found.")

        # Locate the 'Join Room' button within the parent container
        join_button = room_container.find_element(
            By.CSS_SELECTOR,
            "a[href^='/room']",  # Find the <a> tag with href starting with '/room'
        )

        # Click the 'Join Room' button
        join_button.click()
        print("Clicked 'Join Room' button.")
    except Exception as e:
        print(f"Failed to locate or click the 'Join Room' button. Error: {e}")


def click_next_button():
    """
    Click the button after joining the room.
    """
    try:
        # Locate the button by its unique attributes
        next_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button.ring-offset-background.focus-visible\\:ring-ring.inline-flex.items-center.justify-center.gap-2.whitespace-nowrap.rounded-md.px-8.mt-4.text-lg",  # Locate the button by its type
                )
            )
        )

        # Click the button
        next_button.click()
        print("Clicked the next button.")
    except Exception as e:
        print(f"Failed to locate or click the button. Error: {e}")


def switch_to_new_window():
    """
    Switch to the newly opened window.
    """
    try:
        original_window = driver.current_window_handle  # Store the original window
        print(f"Original window: {original_window}")

        # Wait for the new window to open
        # WebDriverWait(driver, 10).until(EC.new_window_is_opened(driver.window_handles))

        # Wait for the number of window handles to increase
        # TODO: Need a more robust handle for this
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

        # Get all window handles
        all_windows = driver.window_handles
        print(f"All windows: {all_windows}")

        # Switch to the new window
        for window in all_windows:
            if window != original_window:
                driver.switch_to.window(window)
                print(f"Switched to new window: {window}")
                break
    except Exception as e:
        print(f"Failed to switch to the new window. Error: {e}")


def check_if_on_game_room():
    """
    Wait for the new game room window and switch to it.
    """
    try:
        switch_to_new_window()  # Switch to the new game room window
        print("minhdz", driver.current_url)
        # Ensure we are on the game room URL
        attempts = 0
        while (
            "https://www.beatcode.dev/game" not in driver.current_url and attempts < 5
        ):
            time.sleep(5)
            print("Waiting for game room to load...")
            attempts += 1

        if "https://www.beatcode.dev/game" in driver.current_url:
            print("Successfully navigated to the game room.")
        else:
            print("Game room did not load in time.")
    except Exception as e:
        print(f"Error while checking for game room. Error: {e}")


def input_code_into_editor(
    code,
    short_line_threshold=30,
    typing_speed_short=0.05,
    typing_speed_long=0.5,
    typo_chance=0.15,
):
    """
    Input code into the editor with realistic typing speed based on line length.

    :param code: The code to be typed.
    :param short_line_threshold: The maximum length for a line to be considered "short".
    :param typing_speed_short: Typing speed (in seconds) for short lines.
    :param typing_speed_long: Typing speed (in seconds) for long lines.
    :param typo_chance: Probability of making a typo.
    """
    try:
        editor_container = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div[role='textbox']",
                )  # Based on the 'role' attribute
            )
        )
        print("Editor container located.")

        # To focus on the code editor
        editor_container.click()
        time.sleep(1)  # Allow the editor to focus a bit

        # Clear existing content in the editor
        editor_container.send_keys(Keys.CONTROL + "a")
        editor_container.send_keys(Keys.DELETE)

        # Type line by line
        lines = code.split("\n")
        for line in lines:
            # Determine typing speed based on line length
            if len(line.strip()) <= short_line_threshold:
                typing_speed = typing_speed_short
            else:
                typing_speed = typing_speed_long

            # Type each character in the line
            for char in line:
                if random.random() < typo_chance:  # Introduce a random typo
                    typo_char = random.choice("abcdefghijklmnopqrstuvwxyz")
                    editor_container.send_keys(typo_char)
                    time.sleep(typing_speed)
                    editor_container.send_keys(Keys.BACKSPACE)  # Correct the typo
                    time.sleep(typing_speed)

                editor_container.send_keys(char)
                time.sleep(random.uniform(typing_speed_short, typing_speed_long))

            # Simulate pressing "Enter" at the end of the line
            editor_container.send_keys(Keys.RETURN)

        print("Code successfully input into the editor with line-based typing speed.")
    except Exception as e:
        print(f"Failed to input code into the editor. Error: {e}")


chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

driver = webdriver.Chrome(service=Service(chrome_driver_path))
wait = WebDriverWait(driver, 10)

code = """class Solution:\ndef repeatedSubstringPattern(self, s: str) -> bool:\nreturn (s + s)[1:-1].find(s) != -1
"""

driver.get("https://www.beatcode.dev/home")

current_url = driver.current_url

if current_url == "https://www.beatcode.dev/home":
    print("You are on the home page")
elif current_url == "https://www.beatcode.dev/login":
    handle_login("kobop54654@halbov.com", "123456789")
    time.sleep(2)
    naviate_to_custom_page()
    time.sleep(1)
    naviate_to_lobby_page()
    time.sleep(1)
    click_join_room()
    time.sleep(1)
    click_next_button()
    time.sleep(5)
    check_if_on_game_room()

    # Successfully got to the game room
    input_code_into_editor(code)
    time.sleep(15)


driver.quit()
