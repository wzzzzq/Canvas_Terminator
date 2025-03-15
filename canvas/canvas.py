from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
from datetime import datetime
import pytz
from time import sleep

from utils.captcha_rec import captcha_rec
from utils.webdriver import init_driver, click_element

def login(driver, user_name, password):
    """Log in to Canvas"""
    # Open website
    driver.get('https://oc.sjtu.edu.cn')
    print(driver.title)
    
    click_element(driver, '#jaccount')
    print("通过#jaccount找到并点击了按钮")
    
    times = 0
    
    while driver.title != "控制面板" and times < 10:
        # Clear and fill username
        userInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'user'))
        )
        userInput.clear()  # Clear existing input
        userInput.send_keys(user_name)
        
        # Clear and fill password
        passwdInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'pass'))
        )
        passwdInput.clear()  # Clear existing input
        passwdInput.send_keys(password)
        
        # Get captcha
        captcha = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'captcha-img'))
        )
        captchaVal = captcha_rec(captcha)
        
        # Clear and fill captcha
        captchaInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'input-login-captcha'))
        )
        captchaInput.clear()  # Clear existing input
        captchaInput.send_keys(captchaVal)
        
        click_element(driver, 'submit-password-button', by='id')
        times += 1
        sleep(1)
    
    assert times < 10, "Failed to login after 10 attempts"
    print("log in successfully")


def find_course(driver, course_name):
    """Find and navigate to a specific course"""
    WebDriverWait(driver, 10).until(EC.title_is("控制面板"))
    
    try:
        course_data = driver.execute_script("return window.ENV;")
        courses = course_data.get("STUDENT_PLANNER_COURSES", [])
        
        course_url = None
        for course in courses:
            if course_name in course.get("shortName", ""):
                course_url = course.get("pagesUrl")
                print(f"Found course: {course['shortName']}")
                print(f"Course URL: {course_url}")
                break
        
        if not course_url:
            raise ValueError(f"Course '{course_name}' not found")
        
        driver.get(course_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ic-app-header__main-navigation"))
        )
        
        quizzes_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='quizzes']"))
        )
        driver.execute_script("arguments[0].click();", quizzes_button)
        print("成功点击了Quizzes按钮")
        
    except Exception as e:
        print(f"Error finding course: {str(e)}")
        raise e

def open_quiz(driver):
        try:
            click_element(driver, '#quiz_show > header > div.take_quiz_button > a')
        except Exception as e:
            print(f"Failed to open quiz: {e}")
def submit_quiz(driver):
    try:
        # Try to click submit button
        click_element(driver, '#submit_quiz_button')
        
        # Handle alert for unanswered questions
        try:
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"Alert detected: {alert_text}")
            alert.accept()  # Click OK
            print("Clicked OK on alert")
        except Exception as e:
            print(f"No alert present or error handling alert: {e}")
            
    except Exception as e:
        print(f"Failed to submit quiz: {e}")

def find_available_quizzes(driver, quiz_name):
    """Find and verify available quizzes
    
    Returns:
        dict: Dictionary mapping quiz titles to their URLs
    """
    quizzes_data = driver.execute_script("return window.ENV;")
    assignments = quizzes_data["QUIZZES"]["assignment"]
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now().astimezone(shanghai_tz)
    
    available_quizzes = {}
    potential_quizzes = {}
    
    # First pass: check basic conditions and get URLs
    for assignment in assignments:
        if quiz_name.lower() in assignment.get('title', '').lower():
            potential_quizzes[assignment['title']] = assignment['html_url']
            print(f"\nFound quiz: {assignment['title']}")
    
    # Second pass: visit each quiz and verify availability
    for title, quiz_url in potential_quizzes.items():
        try:
            driver.get(quiz_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "quiz-header"))
            )
            
            # Get detailed quiz data
            quiz_data = driver.execute_script("return window.ENV;")
            quiz_details = quiz_data.get('QUIZ', {})
            
            # Check conditions
            is_published = quiz_details.get('published', False)
            allowed_attempts = quiz_details.get('allowed_attempts', 0)
            lock_at = quiz_details.get('lock_at')
            
            if lock_at:
                try:
                    lock_time = datetime.fromisoformat(lock_at.replace('Z', '+00:00'))\
                               .astimezone(shanghai_tz)
                except ValueError:
                    lock_time = None
            else:
                lock_time = None
                
            # Verify quiz is available
            if (is_published and 
                (allowed_attempts == -1 or allowed_attempts > 0) and 
                (not lock_time or current_time < lock_time)):
                
                available_quizzes[title] = quiz_url
                
                print(f"\nQuiz is available:")
                print(f"Title: {title}")
                print(f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"Lock time: {lock_time.strftime('%Y-%m-%d %H:%M:%S %Z') if lock_time else 'No lock time'}")
                print(f"Time until lock: {lock_time - current_time if lock_time else 'N/A'}")
                print(f"Attempts allowed: {'Unlimited' if allowed_attempts == -1 else allowed_attempts}")
                
        except Exception as e:
            print(f"Error checking quiz availability: {e}")
            continue
    
    print(f"\nTotal available quizzes found: {len(available_quizzes)}")
    for title, url in available_quizzes.items():
        print(f"- {title}: {url}")
    
    return available_quizzes

def get_quiz_scores(driver):
    """Get current and kept scores from quiz results page
    
    Returns:
        dict: Dictionary with current_score, total_points, and kept_score
    """
    try:
        sleep(1)
        # Find score rows
        score_rows = driver.find_elements(By.CSS_SELECTOR, "table.summary tr")
        if len(score_rows)==0:
            return None
        
        current_score = None
        kept_score = None
        
        for row in score_rows:
            try:
                header = row.find_element(By.TAG_NAME, "th").text.strip()
                value = row.find_element(By.TAG_NAME, "td").text.strip()
                
                if "Current Score:" in header:
                    # Parse "X out of Y" format
                    score, total = map(float, value.split(" out of "))
                    current_score = (score, total)
                    
                elif "Kept Score:" in header:
                    score, total = map(float, value.split(" out of "))
                    kept_score = (score, total)
                    
            except Exception as e:
                print(f"Error parsing score row: {e}")
                continue
        
        if current_score or kept_score:
            print("\nQuiz Scores:")
            if current_score:
                print(f"Current Score: {current_score[0]} out of {current_score[1]}")
            if kept_score:
                print(f"Kept Score: {kept_score[0]} out of {kept_score[1]}")
            
            return {
                'current_score': current_score[0] if current_score else None,
                'total_points': current_score[1] if current_score else None,
                'kept_score': kept_score[0] if kept_score else None
            }
     
        
    except Exception as e:
        print(f"Error getting quiz scores: {e}")
        return None
