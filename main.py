from webdriver import init_driver
from canvas import *
from solve import *

def main():
    driver, user_name, password = init_driver(headless=False)
    try:
        # Login and navigate to quiz
        login(driver, user_name, password)
        find_course(driver, "CHEM")
        available_quizzes = find_available_quizzes(driver, "Pre-Lab")
        
        # Process each quiz
        for title, url in available_quizzes.items():
            try:
                solve_all_quizzes(driver, title, url)
                    
            except Exception as e:
                print(f"Error processing quiz '{title}': {e}")
                continue
            break
                
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()