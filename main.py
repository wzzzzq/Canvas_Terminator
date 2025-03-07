from webdriver import init_driver
from canvas import *
from solve import *
def main():
    driver, user_name, password = init_driver(headless=True)
    try:
        # Login and navigate to quiz
        login(driver, user_name, password)
        find_course(driver, "CHEM")
        urls = find_available_quizzes(driver, "Pre-Lab")
        
        # Process each quiz
        for url in urls:
            # Navigate to quiz and get question
            driver.get(url)
            open_quiz(driver)
            quiz_data = extract_questions_and_options(driver)
            if quiz_data:
                for question in quiz_data:
                    print(f"\nQuestion {question['question_number']}: {question['question_text']}")
                    print("Options:")
                    for i, option in enumerate(question['options'], 1):
                        print(f"{i}. {option}")
                # TODO: Add answer processing logic here
            else:
                print(f"\nFailed to extract question for quiz: {url}")
                
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()