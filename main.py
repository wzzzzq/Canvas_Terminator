from webdriver import init_driver
from canvas import *
from solve import *
import os
from config import *
from localization import get_text

def check_saved_answers(quiz_name):
    """Check if answers exist for the quiz"""
    safe_quiz_name = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).strip()
    json_path = os.path.join(os.path.dirname(__file__), 'correct_answers', f"{safe_quiz_name}.json")
    return os.path.exists(json_path)

def main():
    driver, user_name, password = init_driver(headless=headless)
    try:
        print(get_text("welcome"))
        
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
                print(get_text("no_quizzes", quiz_search))
                continue
                
            print(get_text("found_quizzes", len(available_quizzes)))
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
                        print(f"\n{get_text('processing_quiz', title)}")
                        if has_saved:
                            print(f"1. {get_text('use_saved')}")
                            print(f"2. {get_text('solve_auto')}")
                            print(f"3. {get_text('solve_image')}")
                            print(f"4. {get_text('solve_verify')}")
                            print(f"5. {get_text('skip_quiz')}")
                            print(f"6. {get_text('exit_program')}")
                            choice = input(get_text("enter_choice_saved")).strip()
                            
                            if choice == '6':
                                print(get_text("exiting"))
                                return
                            if choice not in ['1', '2', '3', '4', '5']:
                                print(get_text("invalid_choice"))
                                continue
                            if choice == '5':
                                break
                        else:
                            print(f"1. {get_text('solve_auto')}")
                            print(f"2. {get_text('solve_image')}")
                            print(f"3. {get_text('solve_verify')}")
                            print(f"4. {get_text('skip_quiz')}")
                            print(f"5. {get_text('exit_program')}")
                            choice = input(get_text("enter_choice_no_saved")).strip()
                            
                            if choice == '5':
                                print(get_text("exiting"))
                                return
                            if choice not in ['1', '2', '3', '4']:
                                print(get_text("invalid_choice"))
                                continue
                            if choice == '4':
                                break
                        
                        try:
                            # Process based on user choice
                            if has_saved and choice == '1':
                                print(get_text("loading_answers", title))
                                load_answers(driver, title, url)
                            elif (has_saved and choice == '2') or (not has_saved and choice == '1'):
                                print(get_text("solving_auto", title))
                                solve_all_quizzes(driver, title, image_mode=False)
                            elif (has_saved and choice == '3') or (not has_saved and choice == '2'):
                                print(get_text("solving_image", title))
                                solve_all_quizzes(driver, title, image_mode=True)
                            elif (has_saved and choice == '4') or (not has_saved and choice == '3'):
                                print(get_text("solving_verify", title))
                                solve_one_by_one(driver, title, url, image=False)
                            else:
                                print(get_text("skipping", title))
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