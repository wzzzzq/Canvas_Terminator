from webdriver import init_driver
from canvas import *
from solve import *
import os
from config import *

def check_saved_answers(quiz_name):
    """Check if answers exist for the quiz"""
    safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
    json_path = os.path.join(os.path.dirname(__file__), 'correct_answers', f"{safe_quiz_name}.json")
    return os.path.exists(json_path)

def main():
    driver, user_name, password = init_driver(headless=headless)
    try:
        print("Welcome to the Canvas Quiz Solver!")
        
        while True:
            # Login to Canvas
            login(driver, user_name, password)
            
            course_search = course_name  # From config.py
            quiz_search = quiz_name      # From config.py
            print(f"\nCourse: {course_search}, Quiz: {quiz_search}")
            
            # Navigate and find quizzes
            find_course(driver, course_search)
            available_quizzes = find_available_quizzes(driver, quiz_search)
            
            if not available_quizzes:
                print(f"\nNo available quizzes found matching '{quiz_search}'")
                continue
                
            print(f"\nFound {len(available_quizzes)} available quizzes:")
            for title in available_quizzes.keys():
                print(f"- {title}")
            
            # Process each quiz
            for title, url in available_quizzes.items():
                while True:  # Keep processing until user skips
                    try:
                        has_saved = check_saved_answers(title)
                        driver.get(url)
                        try:
                            get_quiz_scores(driver)
                        except:
                            print("Error getting quiz scores")
                            pass
                        # Prompt user for action
                        print(f"\nProcessing quiz: {title}")
                        if has_saved:
                            print("1. Use saved answers")
                            print("2. Solve with AI (auto mode)")
                            print("3. Solve with AI (image mode)")
                            print("4. Solve one by one (verify each answer)")
                            print("5. Skip this quiz")
                            print("6. Exit program")
                            choice = input("Enter your choice (1-6): ").strip()
                            
                            if choice == '6':
                                print("Exiting program...")
                                return
                            if choice not in ['1', '2', '3', '4', '5']:
                                print("Invalid choice. Please try again.")
                                continue
                            if choice == '5':
                                break
                        else:
                            print("1. Solve with AI (auto mode)")
                            print("2. Solve with AI (image mode)")
                            print("3. Solve one by one (verify each answer)")
                            print("4. Skip this quiz")
                            print("5. Exit program")
                            choice = input("Enter your choice (1-5): ").strip()
                            
                            if choice == '5':
                                print("Exiting program...")
                                return
                            if choice not in ['1', '2', '3', '4']:
                                print("Invalid choice. Please try again.")
                                continue
                            if choice == '4':
                                break
                        
                        try:
                            # Process based on user choice
                            if has_saved and choice == '1':
                                print(f"Loading saved answers for {title}...")
                                load_answers(driver, title, url)
                            elif (has_saved and choice == '2') or (not has_saved and choice == '1'):
                                print(f"Solving {title} with AI in auto mode...")
                                solve_all_quizzes(driver, title, image_mode=False)
                            elif (has_saved and choice == '3') or (not has_saved and choice == '2'):
                                print(f"Solving {title} with AI in image mode...")
                                solve_all_quizzes(driver, title, image_mode=True)
                            elif (has_saved and choice == '4') or (not has_saved and choice == '3'):
                                print(f"Solving {title} one by one, verifying each answer...")
                                solve_one_by_one(driver, title, url, image=False)
                            else:
                                print(f"Skipping {title}")
                                continue
                                
                        except Exception as e:
                            print(f"Error processing quiz '{title}': {e}")
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