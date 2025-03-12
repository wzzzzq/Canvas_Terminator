from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gpt_client_bank import get_gpt_client_dict
import os
from datetime import datetime
from canvas import *
from prompt_bank import *
import json
from config import debug_output, vision_model
from answer_management import save_answers, load_answer_data, save_correct_answers

# Add debug print function
def debug_print(message):
    """Print debug messages if debug_output is enabled"""
    if debug_output:
        print(message)

def extract_questions_and_options(driver, quiz_name, image=False):
    """Extract questions and take screenshots or text based on content"""
    quiz_data = []
    screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots', "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip())
    os.makedirs(screenshot_dir, exist_ok=True)
    
    try:
        sleep(2)
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
                
                # Extract question points
                try:
                    points_element = question_group.find_element(By.CLASS_NAME, "question_points")
                    points = int(points_element.text.strip())
                    debug_print(f"Question {i} points: {points}")
                except Exception as e:
                    points = None
                    debug_print(f"Question {i} has no points information: {e}")
                
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
                
                has_images = has_visible_images or has_hidden_images or image
                
                question_data = {
                    'question_number': i,
                    'type': question_type,
                    'points': points  # Add points to question data
                }
                
                # Extract values for multiple choice or IDs for multiple answers
                values = []
                if question_type == 'multiple_choice_question':
                    options = question_group.find_elements(By.CLASS_NAME, "answer")
                    for j, option in enumerate(options):
                        try:
                            radio = option.find_element(By.CSS_SELECTOR, "input[type='radio']")
                            value = radio.get_attribute("value")
                            values.append(value)
                            debug_print(f"Question {i} option {chr(65+j)}: value={value}")
                        except Exception as e:
                            debug_print(f"Error getting value for option {chr(65+j)}: {e}")
                    # Add values to question data
                    question_data['values'] = values
                    
                elif question_type == 'multiple_answers_question':
                    answers = question_group.find_elements(By.CLASS_NAME, "answer_row")
                    for j, answer in enumerate(answers):
                        try:
                            checkbox = answer.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                            checkbox_id = checkbox.get_attribute("id")
                            values.append(checkbox_id)
                            debug_print(f"Question {i} option {chr(65+j)}: id={checkbox_id}")
                        except Exception as e:
                            debug_print(f"Error getting id for option {chr(65+j)}: {e}")
                    # Add IDs to question data
                    question_data['values'] = values
                
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

def click_answer_option(driver, question_group, response, values):
    """Click the radio button corresponding to the answer choice"""
    # Convert response to index (A=0, B=1, etc.)
    index = ord(response.upper()) - ord('A')
    return click_answers_by_values(driver, question_group, [values[index]])


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

def click_multiple_answers(driver, question_group, response, ids):
    indices = [ord(c.upper()) - ord('A') for c in response if c.isalpha()]
    values = [ids[i] for i in indices]
    return click_multiple_answers_by_ids(driver, question_group, values)
        
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

def solve_all_quizzes(driver, quiz_name, image_mode=True):
    """Solve all available quizzes on the current page"""
    try:
        answers_dir = os.path.join(os.path.dirname(__file__), 'correct_answers')
        safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
        json_path = os.path.join(answers_dir, f"{safe_quiz_name}.json")
        
        debug_print(f"Looking for correct answers file: {json_path}")
        
        answers_dict = {}
        if os.path.exists(json_path):
            # Load answers from JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                answer_data = json.load(f)
                print(f"Successfully loaded correct answers data")
                # Get answers dictionary
                answers_dict = answer_data.get('answers', {})       
 
        open_quiz(driver)
        sleep(2)
        quiz_data = extract_questions_and_options(driver, quiz_name, image=image_mode)
        
        # Initialize GPT client
        client_dict = get_gpt_client_dict()
        
        # Get clients based on config settings
        if vision_model not in client_dict:
            print("Error: Invalid model names in config.py")
            return None
            
        vision_client = client_dict[vision_model]
        print(f"Vision model: {vision_model}")
        
        if quiz_data:
            answers = []
            # Wait for questions to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "question_holder"))
            )
            
            # Get all question holders
            question_holders = driver.find_elements(By.CLASS_NAME, "question_holder")
            vision_client.remove_context()
            
            for question in quiz_data:
                try:
                    # Add quiz name to question data for prompt generation
                    question['quiz_name'] = quiz_name
                    
                    # Get corresponding question group element
                    question_group = question_holders[question['question_number'] - 1]
                    
                    # If answer is already known, fill it
                    if str(question['question_number']) in answers_dict:
                        answer = answers_dict[str(question['question_number'])]
                        fill_question(driver, question_group, answer)
                        print(f"Question {question['question_number']} answered with correct answer: {answer['response']}")
                        answers.append({
                            'question_number': question['question_number'],
                            'type': question['type'],
                            'points': question.get('points'),
                            'response': answer['response'],
                            'value': answer['value']
                        })
                        continue
                    
                    # Solve question using AI
                    answer_data = solve_question_with_ai(driver, question, question_group, vision_client)
                    
                    if answer_data:
                        answers.append(answer_data)
                    else:
                        print(f"Failed to solve question {question['question_number']}")

                except Exception as e:
                    print(f"Error processing question {question['question_number']}: {e}")
                    continue
            
            # After all questions are processed but before submitting
            # Save answers to JSON file
            save_answers(quiz_name, answers)
            
            submit_quiz(driver)
            sleep(2)
            return answers
        else:
            print(f"Failed to extract questions for quiz: {quiz_name}")
            return None
            
    except Exception as e:
        print(f"Error processing quiz '{quiz_name}': {e}")
        return None

def fill_question(driver, question_group, answer):
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
    
def load_answers(driver, quiz_name, url):
    try:
        answer_data = load_answer_data(quiz_name, answer_type="correct_answers")
        if not answer_data:
            return False
        
        # Get answers dictionary
        answers_dict = answer_data.get('answers', {})
        if not answers_dict:
            print("No answers found in JSON file")
            return False
            
        open_quiz(driver)   
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
                        fill_question(driver, question_group, answer)

                    except Exception as e:
                        print(f"Error processing question {question_number}: {e}")
                        continue

                sleep(1)
                print("\nSubmitting quiz...")
                submit_quiz(driver)
                sleep(2)
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
    
def solve_one_by_one(driver, quiz_name, url, image=False):
    """Solve quiz questions one by one, verifying each answer"""
    try:
        # Load any existing correct answers
        correct_answers_dict = {}
        answer_data = load_answer_data(quiz_name, answer_type='correct_answers')
        if answer_data:
            correct_answers_dict = answer_data.get('answers', {})
            print(f"Loaded {len(correct_answers_dict)} existing correct answers")
        
        # Open quiz and extract questions
        open_quiz(driver)
        sleep(2)
        quiz_data = extract_questions_and_options(driver, quiz_name, image=image)
        
        # Initialize GPT client
        client_dict = get_gpt_client_dict()
        vision_client = client_dict[vision_model]
        print(f"Using vision model: {vision_model}")
        vision_client.remove_context()
        
        if not quiz_data:
            print("Failed to extract quiz data")
            return False
            
        # Process each question one by one
        for question in quiz_data:
            driver.get(url)
            vision_client.reset_conversation()
            question_number = question['question_number']
            question_type = question['type']
            points = question.get('points', 0)
            
            print(f"\n----- Question {question_number} ({points} pts) -----")
            
            # If we already have the correct answer, skip this question
            if str(question_number) in correct_answers_dict:
                print(f"Already have correct answer for question {question_number}, skipping")
                continue
            sleep(0.5)
            open_quiz(driver)
            # Get corresponding question element
            question_holders = driver.find_elements(By.CLASS_NAME, "question_holder")
            if question_number > len(question_holders):
                print(f"Question number out of range: {question_number}")
                continue
                
            question_group = question_holders[question_number - 1]
            max_attempts = 5  # Set maximum attempts per question
            wrong_answer = []
            # Try to solve this question until we get it right (or reach max attempts)
            for attempt in range(1, max_attempts + 1):
                try:
                    # Reset the quiz for this question if not the first attempt
                    if attempt > 1:
                        print(f"Retrying question {question_number}, attempt {attempt}")
                        driver.get(url)
                        sleep(0.5)
                        open_quiz(driver)
                        question_holders = driver.find_elements(By.CLASS_NAME, "question_holder")
                        question_group = question_holders[question_number - 1]
                    
                    # Add quiz name to question data
                    question['quiz_name'] = quiz_name

                    # Solve question using AI
                    answer_data = solve_question_with_ai(driver, question, question_group, vision_client, add_to_history=True, retry=(attempt>1), wrong_answer = wrong_answer)
                    if question_type == 'text_only_question':
                        break

                    if not answer_data:
                        print("Failed to get valid answer, retrying...")
                        continue
                    
                    # Submit quiz and check score
                    print("Submitting quiz...")
                    submit_quiz(driver)
                    sleep(1)
                    
                    # Check score
                    scores = get_quiz_scores(driver)
                    if not scores or 'current_score' not in scores:
                        print("Couldn't retrieve scores")
                        continue
                        
                    # Consider answer correct if we got full points for this question
                    if scores['current_score'] >= points:
                        print(f"✓ CORRECT! Got {scores['current_score']} points")
                        
                        # Save to correct answers file
                        correct_answers_dict[str(question_number)] = {
                            'type': question_type,
                            'points': points,
                            'response': answer_data['response'],
                            'value': answer_data['value']
                        }
                        
                        # Update correct answers file
                        save_correct_answers(quiz_name, correct_answers_dict)
                        
                        # Break the retry loop for this question
                        break
                    else:
                        print(f"✗ INCORRECT. Got {scores['current_score']} out of {points} points")
                        wrong_answer.append(answer_data['response'])
                        
                        # If this was the last attempt, move on
                        if attempt == max_attempts:
                            print(f"Max attempts reached for question {question_number}")
                        
                
                except Exception as e:
                    print(f"Error processing question {question_number}, attempt {attempt}: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error in solve_one_by_one: {e}")
        return False

def solve_question_with_ai(driver, question, question_group, ai_client, add_to_history=False, retry=False, wrong_answer = None):
    """
    Use AI to solve a single question and fill in the answer
    
    Args:
        driver: Selenium WebDriver instance
        question: Dictionary with question data
        question_group: WebElement representing the question
        ai_client: AI client instance to use
    
    Returns:
        dict: Answer data or None if failed
    """
    try:
        question_number = question['question_number']
        question_type = question['type']
        points = question.get('points', 0)
        
        if retry:
            print(f"Retrying question {question_number}")
            response = ai_client.send_text(get_feedback_prompt(wrong_answer=wrong_answer), max_tokens=50, add_to_history=True)
        else:
            # Get AI response to the question
            if question.get('has_images', True):
                prompt = get_prompt_image(question.get('quiz_name', ''), question_type)
                # Create context for next question if needed
                if question_type == 'text_only_question':
                    ai_client.create_context(prompt, question['screenshot_path'] if question.get('has_images') else None)
                    return None
                response = ai_client.send_image(
                    prompt, 
                    question['screenshot_path'], 
                    max_tokens=256, 
                    add_to_history=add_to_history
                )
            else:
                prompt = get_prompt_text(
                    question.get('quiz_name', ''),
                    question_type, 
                    question['question_text'], 
                    question['answers']
                )
                # Create context for next question if needed
                if question_type == 'text_only_question':
                    ai_client.create_context(prompt, question['screenshot_path'] if question.get('has_images') else None)
                    return None
                response = ai_client.send_text(prompt, max_tokens=256, add_to_history=add_to_history)
        
        print(f"AI response for Q{question_number}: {response}")
        answer_data = None
        # Process response based on question type
        if question_type == 'multiple_choice_question':
            response = response.strip().upper()
            if response and len(response) == 1:  # Single letter response
                value = click_answer_option(driver, question_group, response, question['values'])
                answer_data = {
                    'question_number': question_number,
                    'type': question_type,
                    'points': points,
                    'response': response,
                    'value': value
                }
                print(f"Question {question_number} ({points} pts): Selected option {response}")
            else:
                print(f"Invalid response format for Q{question_number}: {response}")
                return None

        elif question_type == 'multiple_answers_question':
            response = response.strip().upper()
            if response and all(c.isalpha() for c in response):
                ids = click_multiple_answers(driver, question_group, response, question['values'])
                answer_data = {
                    'question_number': question_number,
                    'type': question_type,
                    'points': points,
                    'response': response,
                    'value': ids
                }
                print(f"Question {question_number} ({points} pts): Selected options {response}")
            else:
                print(f"Invalid response format for Q{question_number}: {response}")
                return None
        
        elif question_type == 'numerical_question':
            response = response.strip()
            if response and any(char.isdigit() for char in response):
                input_field = question_group.find_element(
                    By.CSS_SELECTOR, 
                    "input.numerical_question_input"
                )
                input_field.clear()
                input_field.send_keys(response)
                value = input_field.get_attribute("value")
                answer_data = {
                    'question_number': question_number,
                    'type': question_type,
                    'points': points,
                    'response': response,
                    'value': [value] if value else []
                }
                print(f"Question {question_number} ({points} pts): Entered value {value}")
            else:
                print(f"Invalid numerical response for Q{question_number}: {response}")
                return None
                
        elif question_type == 'fill_in_multiple_blanks_question':
            response = response.strip()
            if response and ' ' in response:
                input_fields = question_group.find_elements(
                    By.CSS_SELECTOR, 
                    "input.question_input[type='text']"
                )
                answers_list = response.split()
                values = []
                
                for input_field, answer_text in zip(input_fields, answers_list):
                    input_field.clear()
                    input_field.send_keys(answer_text)
                    value = input_field.get_attribute("value")
                    if value:
                        values.append(value)
                        
                answer_data = {
                    'question_number': question_number,
                    'type': question_type,
                    'points': points,
                    'response': response,
                    'value': values
                }
                print(f"Question {question_number} ({points} pts): Filled blanks with {values}")
            else:
                print(f"Invalid format for fill-in-blanks Q{question_number}: {response}")
                return None
                
        else:
            print(f"Unsupported question type for Q{question_number}: {question_type}")
            return None
            
        return answer_data
        
    except Exception as e:
        print(f"Error solving question {question.get('question_number', '?')}: {e}")
        return None


