from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gpt_client_bank import get_gpt_client_dict
import os
from datetime import datetime
from canvas import *
from prompt_bank import *
import json
from config import debug_output

# Add debug print function
def debug_print(message):
    """Print debug messages if debug_output is enabled"""
    if debug_output:
        print(message)

def extract_questions_and_options(driver, quiz_name):
    """Extract questions and take screenshots or text based on content"""
    quiz_data = []
    screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots', quiz_name.strip())
    os.makedirs(screenshot_dir, exist_ok=True)
    
    try:
        question_groups = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "question_holder"))
        )
        
        for i, question_group in enumerate(question_groups, 1):
            try:
                # Get question type
                display_question = question_group.find_element(By.CLASS_NAME, "display_question")
                class_list = display_question.get_attribute("class").split()
                question_type = next((cls for cls in class_list 
                                   if cls not in ["display_question", "question"]), "unknown")
                
                # Check for images in visible and hidden content
                has_visible_images = bool(
                    question_group.find_elements(By.TAG_NAME, "img") or
                    question_group.find_elements(By.CLASS_NAME, "equation_image")
                )
                
                # Check for images in hidden textarea
                textarea = question_group.find_element(
                    By.CSS_SELECTOR, 
                    "textarea.textarea_question_text"
                ).get_attribute("innerHTML")
                has_hidden_images = "equation_image" in textarea or "<img" in textarea
                
                has_images = has_visible_images or has_hidden_images
                
                question_data = {
                    'question_number': i,
                    'type': question_type,
                }
                
                if has_images:
                    debug_print(f"Question {i} contains images")
                    # Take screenshot for questions with images
                    driver.execute_script("arguments[0].scrollIntoView(true);", question_group)
                    sleep(0.5)
                    screenshot_path = os.path.join(screenshot_dir, f'question_{i}.png')
                    question_group.screenshot(screenshot_path)
                    question_data['screenshot_path'] = screenshot_path
                    question_data['has_images'] = True
                    
                else:
                    # Extract text from specific question text div
                    question_text_div = question_group.find_element(
                        By.CSS_SELECTOR, 
                        "div.question_text.user_content"
                    )
                    question_text = question_text_div.text.strip()
                
                    # Get answer options
                    answers = []
                    for answer in question_group.find_elements(By.CLASS_NAME, "answer"):
                        answer_text = answer.find_element(
                            By.CLASS_NAME, "answer_label"
                        ).text.strip()
                        
                        answers.append(answer_text)
                    
                    question_data.update({
                        'has_images': False,
                        'question_text': question_text,
                        'answers': answers
                    })
                    debug_print(f"Question {i} text: {question_text}")
                    debug_print(f"Question {i} answers: {answers}")
                
                quiz_data.append(question_data)
                debug_print(f"Processed question {i}: {'screenshot' if has_images else 'text'} mode")
                
            except Exception as e:
                print(f"Error processing question {i}: {e}")
                
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

def click_multiple_answers(driver, question_group, response):
    try:
        ids = []
        answers = question_group.find_elements(By.CLASS_NAME, "answer_row")
        indices = [ord(c.upper()) - ord('A') for c in response if c.isalpha()]
        
        for index in indices:
            if 0 <= index < len(answers):
                try:
                    checkbox = answers[index].find_element(
                        By.CSS_SELECTOR, 
                        "input[type='checkbox']"
                    )
                    checkbox_id = checkbox.get_attribute("id")
                    checkbox.click()
                    ids.append(checkbox_id)
                    debug_print(f"Clicked option {chr(index + ord('A'))} with ID: {checkbox_id}")
                except Exception as e:
                    debug_print(f"Error clicking checkbox {chr(index + ord('A'))}: {e}")
            else:
                debug_print(f"Invalid answer index: {index}")
                
        return ids
            
    except Exception as e:
        debug_print(f"Error in click_multiple_answers: {e}")
        return []

def click_multiple_answers_by_ids(driver, question_group, ids):
    try:
        clicked_ids = []
        
        # Click each checkbox with matching ID
        for checkbox_id in ids:
            try:
                checkbox = question_group.find_element(By.ID, checkbox_id)
                checkbox.click()
                clicked_ids.append(checkbox_id)
                print(f"Clicked checkbox with ID: {checkbox_id}")
            except Exception as e:
                print(f"Error clicking checkbox with ID {checkbox_id}: {e}")
                
        return clicked_ids
            
    except Exception as e:
        print(f"Error in click_multiple_answers_by_ids: {e}")
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
        
        # Prompt user for model selections
        models = list(client_dict.keys())
        print("\nAvailable models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
            
        # Select model for text questions
        while True:
            try:
                text_selection = int(input("\nEnter number of model to use for TEXT questions: "))
                if 1 <= text_selection <= len(models):
                    text_model = models[text_selection-1]
                    break
                print("Invalid number. Please enter a number between 1 and", len(models))
            except ValueError:
                print("Please enter a valid number")
        
        # Select model for vision questions
        while True:
            try:
                vision_selection = int(input("\nEnter number of model to use for VISION questions: "))
                if 1 <= vision_selection <= len(models):
                    vision_model = models[vision_selection-1]
                    break
                print("Invalid number. Please enter a number between 1 and", len(models))
            except ValueError:
                print("Please enter a valid number")
        
        text_client = client_dict[text_model]
        vision_client = client_dict[vision_model]
        
        if quiz_data:
            answers = []
            # Wait for questions to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "question_holder"))
            )
            
            # Get all question holders
            question_holders = driver.find_elements(By.CLASS_NAME, "question_holder")
            text_client.reset_conversation()
            vision_client.reset_conversation()
            
            for question in quiz_data:
                try:
                    # Get corresponding question group element
                    question_group = question_holders[question['question_number'] - 1]
                    
                    # Choose client based on whether question has images
                    if question.get('has_images', True):
                        client = vision_client
                        prompt = get_prompt_image(quiz_name, question['type'])
                        response = client.send_image(prompt, question['screenshot_path'], max_tokens=256)
                    else:
                        client = text_client
                        prompt = get_prompt_text(quiz_name, question['type'], 
                                              question['question_text'], 
                                              question['answers'])
                        response = client.send_text(prompt, max_tokens=256)
                    
                    debug_print(f"\nQuestion {question['question_number']} ({question['type']}):")
                    debug_print(f"Using model: {vision_model if question.get('has_images', True) else text_model}")
                    debug_print(f"Response: {response}")
                    
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
                            # Click checkboxes by letter response and get IDs
                            ids = click_multiple_answers(driver, question_group, response)
                            answers.append({
                                'question_number': question['question_number'],
                                'type': question['type'],
                                'response': response,
                                'value': ids  # Store checkbox IDs
                            })
                            print(f"Question {question['question_number']} answered with selections: {response}")
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
                    elif question['type'] == 'fill_in_multiple_blanks_question':
                        response = response.strip()
                        if response and ' ' in response:  # Check for space-separated values
                            # Find all input fields
                            input_fields = question_group.find_elements(
                                By.CSS_SELECTOR, 
                                "input.question_input[type='text']"
                            )
                            
                            # Split response into separate answers
                            answers_list = response.split()
                            values = []
                            
                            # Fill each blank with corresponding answer
                            for input_field, answer in zip(input_fields, answers_list):
                                input_field.clear()
                                input_field.send_keys(answer)
                                value = input_field.get_attribute("value")
                                if value:
                                    values.append(value)
                            
                            # Record answer info
                            answers.append({
                                'question_number': question['question_number'],
                                'type': question['type'],
                                'response': response,
                                'value': values  # Store as list
                            })
                            print(f"Question {question['question_number']} answered: {response}")
                        else:
                            print(f"Invalid response format for question {question['question_number']}: {response}")

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
    try:
        answers_dir = os.path.join(os.path.dirname(__file__), 'answers')
        safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
        json_path = os.path.join(answers_dir, f"{safe_quiz_name}.json")
        
        debug_print(f"Looking for answers file: {json_path}")
        
        if not os.path.exists(json_path):
            print(f"Answers file not found: {json_path}")  # Keep critical errors
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
                        debug_print(f"\nProcessing question {question_number}")
                        # Get corresponding question group element
                        q_index = int(question_number) - 1
                        if q_index >= len(question_holders):
                            print(f"Question index out of range: {q_index}")
                            continue
                            
                        question_group = question_holders[q_index]
                        
                        # Scroll question into view
                        driver.execute_script("arguments[0].scrollIntoView(true);", question_group)
                        sleep(0.5)  # Small delay after scrolling
                        
                        if answer['type'] == 'multiple_choice_question':
                            print(f"Answering multiple choice with value: {answer['value']}")
                            clicked_value = click_answers_by_values(driver, question_group, answer['value'])
                            print(f"Successfully clicked value: {clicked_value}")
                        
                        elif answer['type'] == 'multiple_answers_question':
                            debug_print(f"Answering multiple answers with IDs: {answer['value']}")
                            clicked_ids = click_multiple_answers_by_ids(driver, question_group, answer['value'])
                            debug_print(f"Successfully clicked IDs: {clicked_ids}")
                        
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
                        
                        elif answer['type'] == 'fill_in_multiple_blanks_question':
                            values = answer['value']
                            # Find all text input fields
                            input_fields = question_group.find_elements(
                                By.CSS_SELECTOR, 
                                "input.question_input[type='text']"
                            )
                            
                            debug_print(f"Filling {len(values)} values into {len(input_fields)} blanks")
                            
                            # Fill each blank with corresponding value
                            for input_field, value in zip(input_fields, values):
                                input_field.clear()
                                input_field.send_keys(value)
                                entered_value = input_field.get_attribute("value")
                                print(f"Entered value: {entered_value}")
                        
                    except Exception as e:
                        print(f"Error processing question {question_number}: {e}")
                        continue
                sleep(1)
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
