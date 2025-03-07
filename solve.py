from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_questions_and_options(driver):
    """Extract all questions and their options from Canvas quiz page"""
    quiz_data = []
    try:
        # Wait for quiz content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question_holder"))
        )
        
        # Find all question groups
        question_groups = driver.find_elements(By.CLASS_NAME, "question_holder")
        
        for i, question_group in enumerate(question_groups, 1):
            try:
                # Extract question text
                question_text = question_group.find_element(
                    By.CLASS_NAME,
                    "user_content"
                ).text.strip()
                
                # Extract question type
                type_element = question_group.find_element(
                    By.CLASS_NAME,
                    "question_type"
                )
                question_type = type_element.text.strip()
                
                # Extract options using answer_label class
                options = []
                try:
                    option_elements = question_group.find_elements(
                        By.CLASS_NAME,
                        "answer_label"
                    )
                    
                    for option in option_elements:
                        option_text = option.text.strip()
                        if option_text:  # Only add non-empty options
                            options.append(option_text)
                except Exception as e:
                    print(f"No options found for question {i}")
                
                # Determine if it's a choice question based on options presence
                question_type = "choice" if options else "open"
                
                # Store question and its options
                quiz_data.append({
                    'question_number': i,
                    'question_text': question_text,
                    'options': options,
                    'type': question_type
                })
                
                print(f"\nQuestion {i}: {question_text}")
                print("Options:")
                for j, opt in enumerate(options, 1):
                    print(f"{j}. {opt}")
                
            except Exception as e:
                print(f"Error extracting question {i}: {e}")
                continue
        
        if not quiz_data:
            print("No questions found")
            return None
        
        print(f"\nTotal questions found: {len(quiz_data)}")
        return quiz_data

    except Exception as e:
        print(f"Failed to extract questions and options: {e}")
        return None