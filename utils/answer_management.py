import os
import json
from datetime import datetime
from config import debug_output

def check_saved_answers(quiz_name):
    """Check if answers exist for the quiz"""
    safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
    json_path = os.path.join(os.path.dirname(__file__), 'correct_answers', f"{safe_quiz_name}.json")
    return os.path.exists(json_path)

def debug_print(message):
    """Print debug messages if debug_output is enabled"""
    if debug_output:
        print(message)

def save_answers(quiz_name, answers):
    """
    Save quiz answers to a JSON file
    
    Args:
        quiz_name (str): Name of the quiz
        answers (list): List of answer dictionaries
        
    Returns:
        str: Path to the saved JSON file or None on failure
    """
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
                'points': answer.get('points'),
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
        return json_path
    
    except Exception as e:
        print(f"Error saving answers to JSON: {e}")
        return None

def load_answer_data(quiz_name, answer_type='answers'):
    """
    Load answer data from JSON file
    
    Args:
        quiz_name (str): Name of the quiz
        answer_type (str): Type of answers to load ('answers' or 'correct_answers')
        
    Returns:
        dict: Dictionary of answers or None if file doesn't exist
    """
    try:
        # Determine the directory based on answer_type
        if answer_type == 'correct_answers':
            answers_dir = os.path.join(os.path.dirname(__file__), 'correct_answers')
        else:
            answers_dir = os.path.join(os.path.dirname(__file__), 'answers')
            
        safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
        json_path = os.path.join(answers_dir, f"{safe_quiz_name}.json")
        
        debug_print(f"Looking for {answer_type} file: {json_path}")
        
        if not os.path.exists(json_path):
            print(f"{answer_type.capitalize()} file not found: {json_path}")
            return None
        
        # Load answers from JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            answer_data = json.load(f)
            debug_print(f"Successfully loaded {answer_type} data")
            return answer_data
    
    except Exception as e:
        print(f"Error loading {answer_type}: {e}")
        return None

def save_correct_answers(quiz_name, correct_answers_dict):
    """
    Save correct quiz answers to a JSON file
    
    Args:
        quiz_name (str): Name of the quiz
        correct_answers_dict (dict): Dictionary of correct answers
        
    Returns:
        str: Path to the saved JSON file or None on failure
    """
    try:
        # Create correct answers directory if it doesn't exist
        correct_answers_dir = os.path.join(os.path.dirname(__file__), 'correct_answers')
        os.makedirs(correct_answers_dir, exist_ok=True)
        
        # Create filename with quiz name
        safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
        correct_json_path = os.path.join(correct_answers_dir, f"{safe_quiz_name}.json")
        
        # Create answer data structure
        correct_data = {
            'quiz_name': quiz_name,
            'timestamp': datetime.now().isoformat(),
            'answers': correct_answers_dict
        }
        
        # Write to JSON file
        with open(correct_json_path, 'w', encoding='utf-8') as f:
            json.dump(correct_data, f, indent=2)
        print(f"Correct answers saved to: {correct_json_path}")
        return correct_json_path
    
    except Exception as e:
        print(f"Error saving correct answers to JSON: {e}")
        return None
