from webdriver import init_driver
from canvas import *
from solve import *
import os
from config import *

def check_saved_answers(quiz_name):
    """Check if answers exist for the quiz"""
    safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
    json_path = os.path.join(os.path.dirname(__file__), 'answers', f"{safe_quiz_name}.json")
    return os.path.exists(json_path)

def main():
    driver, user_name, password = init_driver(headless=headless)
    try:
        print("Welcome to the Canvas Quiz Solver!")
        # Login to Canvas
        login(driver, user_name, password)
        
        # Prompt for course and quiz search terms
        course_search = input("\nEnter course name or prefix (e.g., CHEM): ").strip()
        quiz_search = input("Enter quiz name or prefix (e.g., Pre-Lab): ").strip()
        
        # Navigate and find quizzes
        find_course(driver, course_search)
        available_quizzes = find_available_quizzes(driver, quiz_search)
        
        if not available_quizzes:
            print(f"\nNo available quizzes found matching '{quiz_search}'")
            return
            
        print(f"\nFound {len(available_quizzes)} available quizzes:")
        for title in available_quizzes.keys():
            print(f"- {title}")
        
        # Process each quiz
        for title, url in available_quizzes.items():
            try:
                has_saved = check_saved_answers(title)
                
                # Prompt user for action
                print(f"\nProcessing quiz: {title}")
                if has_saved:
                    print("1. Use saved answers")
                    print("2. Solve with AI")
                    print("3. Skip this quiz")
                    choice = input("Enter your choice (1-3): ").strip()
                else:
                    print("1. Solve with AI")
                    print("2. Skip this quiz")
                    choice = input("Enter your choice (1-2): ").strip()
                
                # Process based on user choice
                if has_saved and choice == '1':
                    print(f"Loading saved answers for {title}...")
                    load_answers(driver, title, url)
                elif (has_saved and choice == '2') or (not has_saved and choice == '1'):
                    print(f"Solving {title} with AI...")
                    solve_all_quizzes(driver, title, url)
                else:
                    print(f"Skipping {title}")
                    continue
                    
            except Exception as e:
                print(f"Error processing quiz '{title}': {e}")
                continue
                
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()