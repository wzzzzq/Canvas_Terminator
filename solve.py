from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gpt_client_bank import get_gpt_client_dict
import os
from datetime import datetime
from canvas import *
from prompt_bank import *
import json

def extract_questions_and_options(driver, quiz_name):
    """Extract all questions and their options from Canvas quiz page and save screenshots"""
    quiz_data = []
    
    # Create screenshots directory with sanitized quiz name
    safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
    screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots', safe_quiz_name)
    os.makedirs(screenshot_dir, exist_ok=True)
    
    try:
        # Wait for quiz content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question_holder"))
        )
        
        # Find all question groups
        question_groups = driver.find_elements(By.CLASS_NAME, "question_holder")
        
        for i, question_group in enumerate(question_groups, 1):
            try:
                # Find question type from display_question div classes
                display_question = question_group.find_element(By.CLASS_NAME, "display_question")
                class_list = display_question.get_attribute("class").split()
                # Filter out common classes to get the specific question type
                question_type = next((cls for cls in class_list 
                                   if cls not in ["display_question", "question"]), "unknown")
                #print(f"Question {i} type: {question_type}")
                
                # Scroll element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", question_group)
                
                # Wait for element to be fully visible
                WebDriverWait(driver, 5).until(
                    lambda x: question_group.is_displayed()
                )
                
                # Take screenshot of question
                screenshot_path = os.path.join(screenshot_dir, f'question_{i}.png')
                question_group.screenshot(screenshot_path)
                
                # Store question data
                question_data = {
                    'question_number': i,
                    'type': question_type,
                    'screenshot_path': screenshot_path
                }
                quiz_data.append(question_data)
                
            except Exception as e:
                print(f"Error processing question {i}: {e}")
                continue
        
        return quiz_data
        
    except Exception as e:
        print(f"Failed to process quiz: {e}")
        return None

def click_answer_option(driver, question_group, response):
    """Click the radio button corresponding to the answer choice"""
    try:
        # Find all answer options in this question group
        options = question_group.find_elements(By.CLASS_NAME, "answer")
        
        # Convert response to index (A=0, B=1, etc.)
        index = ord(response.upper()) - ord('A')
        
        if 0 <= index < len(options):
            # Find and click the radio button
            radio = options[index].find_element(By.CSS_SELECTOR, "input[type='radio']")
            value = radio.get_attribute("value")
            radio.click()
            print(f"Clicked option {response} with value: {value}")
            return value
        else:
            print(f"Invalid answer index: {index} for response: {response}")
            return None
            
    except Exception as e:
        print(f"Error clicking answer option: {e}")
        return None

def click_answers_by_values(driver, question_group, values):
    """Click radio buttons or checkboxes with matching values
    
    Args:
        driver: Selenium WebDriver instance
        question_group: WebElement representing the question container
        values: List of values to match with input values
    
    Returns:
        list: List of successfully clicked input values
    """
    try:
        clicked_values = []
        # Find all radio/checkbox inputs in this question group
        inputs = question_group.find_elements(
            By.CSS_SELECTOR, 
            "input[type='radio'], input[type='checkbox']"
        )
        
        # Click each input that matches a value in the list
        for input_element in inputs:
            value = input_element.get_attribute("value")
            if value in values:
                input_element.click()
                clicked_values.append(value)
                print(f"Clicked option with value: {value}")
        
        if not clicked_values:
            print(f"No matching options found for values: {values}")
        return clicked_values
            
    except Exception as e:
        print(f"Error clicking answers by values: {e}")
        return []

def solve_all_quizzes(driver, quiz_name, url):
    """Solve all available quizzes on the current page"""
    try:
        # Navigate to quiz and get questions
        driver.get(url)
        open_quiz(driver)
        
        quiz_data = extract_questions_and_options(driver, quiz_name)
        # Initialize GPT client
        client_dict = get_gpt_client_dict()
        client = client_dict["GLM-4"]
        
        if quiz_data:
            answers = []
            # Wait for questions to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "question_holder"))
            )
            
            # Get all question holders
            question_holders = driver.find_elements(By.CLASS_NAME, "question_holder")
            
            for question in quiz_data:
                try:
                    # Get corresponding question group element
                    question_group = question_holders[question['question_number'] - 1]
                    
                    # Get and process response
                    prompt = get_prompt_bank(quiz_name, question['type'])
                    response = client.send_image_with_history(prompt, question['screenshot_path'], max_tokens=256)
                    print(f"Question {question['question_number']} response: {response}")
                    
                    if question['type'] == 'multiple_choice_question':
                        response = response.strip().upper()
                        if response and len(response) == 1:  # Ensure response is a single letter
                            # Click the answer and record info
                            value = click_answer_option(driver, question_group, response)
                            answers.append({
                                'question_number': question['question_number'],
                                'type': question['type'],
                                'response': response,
                                'value': [value] if value else []  # Store as list
                            })
                            print(f"Question {question['question_number']} answered: {response}")
                        else:
                            print(f"Invalid response format for question {question['question_number']}: {response}")

                    elif question['type'] == 'multiple_answers_question':
                        response = response.strip().upper()
                        if response and all(c.isalpha() for c in response):
                            # Click the answers and record info
                            values = []
                            for answer in response:
                                value = click_answer_option(driver, question_group, answer)
                                if value:
                                    values.append(value)
                            answers.append({
                                'question_number': question['question_number'],
                                'type': question['type'],
                                'response': response,
                                'value': values  # Already a list
                            })
                            print(f"Question {question['question_number']} answered: {response}")
                        else:
                            print(f"Invalid response format for question {question['question_number']}: {response}")
                    
                    elif question['type'] == 'numerical_question':
                        response = response.strip()
                        if response and any(char.isdigit() for char in response):
                            # Find and fill numerical input
                            input_field = question_group.find_element(
                                By.CSS_SELECTOR, 
                                "input.numerical_question_input"
                            )
                            input_field.clear()
                            input_field.send_keys(response)
                            
                            # Record answer info
                            value = input_field.get_attribute("value")
                            answers.append({
                                'question_number': question['question_number'],
                                'type': question['type'],
                                'response': response,
                                'value': [value] if value else []  # Store as list
                            })
                            print(f"Question {question['question_number']} answered: {response}")
                        else:
                            print(f"Invalid numerical response for question {question['question_number']}: {response}")

                except Exception as e:
                    print(f"Error processing question {question['question_number']}: {e}")
                    continue
            
            # After all questions are processed but before submitting
            # Save answers to JSON file
            try:
                # Create answers directory if it doesn't exist
                answers_dir = os.path.join(os.path.dirname(__file__), 'answers')
                os.makedirs(answers_dir, exist_ok=True)
                
                # Create filename with quiz name
                safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
                json_path = os.path.join(answers_dir, f"{safe_quiz_name}.json")
                
                # Convert answers list to dictionary with question numbers as keys
                answers_dict = {
                    str(answer['question_number']): {
                        'type': answer['type'],
                        'response': answer['response'],
                        'value': answer['value']
                    } for answer in answers
                }
                
                # Create answer data structure
                answer_data = {
                    'quiz_name': quiz_name,
                    'timestamp': datetime.now().isoformat(),
                    'answers': answers_dict
                }
                
                # Write to JSON file
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(answer_data, f, indent=2)
                print(f"Answers saved to: {json_path}")
            
            except Exception as e:
                print(f"Error saving answers to JSON: {e}")
            
            submit_quiz(driver)
            sleep(10)
            return answers
        else:
            print(f"Failed to extract questions for quiz: {quiz_name}")
            return None
            
    except Exception as e:
        print(f"Error processing quiz '{quiz_name}': {e}")
        return None

def load_answers(driver, quiz_name, url):
    """Load answers from JSON file and submit them"""
    try:
        # Create answers directory if it doesn't exist
        answers_dir = os.path.join(os.path.dirname(__file__), 'answers')
        safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
        json_path = os.path.join(answers_dir, f"{safe_quiz_name}.json")
        
        print(f"Looking for answers file: {json_path}")
        
        if not os.path.exists(json_path):
            print(f"Answers file not found: {json_path}")
            return False
        
        # Load answers from JSON file
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                answer_data = json.load(f)
                print(f"Successfully loaded answers data")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file: {e}")
            return False
        except Exception as e:
            print(f"Error reading answers file: {e}")
            return False
        
        # Get answers dictionary
        answers_dict = answer_data.get('answers', {})
        if not answers_dict:
            print("No answers found in JSON file")
            return False

        print(f"Navigating to quiz URL: {url}")
        driver.get(url)
        
        print("Opening quiz...")
        try:
            open_quiz(driver)
        except Exception as e:
            print(f"Error opening quiz: {e}")
            return False
        
        if answers_dict:
            try:
                # Wait for questions to load
                print("Waiting for questions to load...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "question_holder"))
                )
                
                # Get all question holders
                question_holders = driver.find_elements(By.CLASS_NAME, "question_holder")
                print(f"Found {len(question_holders)} questions")
                
                for question_number, answer in answers_dict.items():
                    try:
                        print(f"\nProcessing question {question_number}")
                        # Get corresponding question group element
                        q_index = int(question_number) - 1
                        if q_index >= len(question_holders):
                            print(f"Question index out of range: {q_index}")
                            continue
                            
                        question_group = question_holders[q_index]
                        
                        # Scroll question into view
                        driver.execute_script("arguments[0].scrollIntoView(true);", question_group)
                        sleep(0.5)  # Small delay after scrolling
                        
                        if answer['type'] in ['multiple_choice_question', 'multiple_answers_question']:
                            print(f"Answering {answer['type']} with values: {answer['value']}")
                            clicked_values = click_answers_by_values(driver, question_group, answer['value'])
                            print(f"Successfully clicked values: {clicked_values}")
                        
                        elif answer['type'] == 'numerical_question':
                            value = answer['value'][0] if answer['value'] else None
                            if value:
                                print(f"Entering numerical value: {value}")
                                input_field = question_group.find_element(
                                    By.CSS_SELECTOR, 
                                    "input.numerical_question_input"
                                )
                                input_field.clear()
                                input_field.send_keys(value)
                                print(f"Successfully entered value: {value}")
                    
                    except Exception as e:
                        print(f"Error processing question {question_number}: {e}")
                        continue
                
                print("\nSubmitting quiz...")
                submit_quiz(driver)
                sleep(10)
                return True
                
            except Exception as e:
                print(f"Error processing questions: {e}")
                return False
                
        else:
            print(f"No answers found for quiz: {quiz_name}")
            return False
            
    except Exception as e:
        print(f"Error loading answers: {e}")
        return False
