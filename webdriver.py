from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
from time import sleep

def init_driver(headless=False):
    """Initialize and return a Chrome WebDriver"""
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    user_name = os.getenv('JACCOUNT_USERNAME')
    password = os.getenv('JACCOUNT_PASSWORD')
    
    if not user_name or not password:
        raise ValueError("Missing credentials in .env file")
    
    options = Options()
    if headless:
        options.add_argument("-headless")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    sleep(1)
    zoom_out= "document.body.style.zoom='0.5'"
    driver.execute_script(zoom_out)
    sleep(1)
    return driver, user_name, password

def click_element(driver, element, by='css selector', timeout=10):
    """Helper function for stable clicking"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR if by == 'css selector' else By.ID, element))
        )
        elem = driver.find_element(by, element)
        driver.execute_script("arguments[0].click();", elem)
    except Exception as e:
        print(f"Failed to click element: {element}")
        raise e