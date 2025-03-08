def get_prompt_bank(quiz_name, question_type):
    prompt_bank = {
        'multiple_choice_question': f"""
        You are given a multiple-choice question on the subject of {quiz_name} in the image attached. Please carefully analyze the image and respond with ONLY the letter corresponding to the correct answer (e.g., 'A', 'B', 'C', etc.). Do not provide any additional text, explanations, or reasoning—just the letter of the correct answer.
        Only the letter of the correct answer is required. Respond with 'A', 'B', 'C', 'D', etc., nothing more.
        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        OUTPUT EXAMPLE: 'A', 'B', 'C', 'D', etc.
        """,

        'multiple_answers_question': f"""
        You are given a multiple-answers question on the subject of {quiz_name} in the image attached. One or more answers may be correct. Please carefully analyze the image and respond with ONLY the letters corresponding to the correct answers in ascending order (e.g., 'AB', 'BCD', 'AC', etc.). Do not provide any additional text, explanations, or reasoning—just the letters of the correct answers.
        Only the letters of the correct answers are required. Respond with combinations of 'A', 'B', 'C', 'D', etc., nothing more.
        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        OUTPUT EXAMPLE: 'AB', 'BCD', 'AC', etc.
        """,
        
        'numerical_question': f"""
        You are given a numerical question on the subject of {quiz_name} in the image attached. Please carefully analyze the image and respond with ONLY the numerical value of the correct answer (e.g., '1.20', '3.2', '4', etc.). Do not provide any additional text, explanations, or reasoning—just the numerical value of the correct answer.
        Only the numerical value of the correct answer is required. Respond with '1', '2', '3', etc., nothing more.
        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        OUTPUT EXAMPLE: '1', '2.4', '3', etc.
        """,

        'text_only_question': f"""
        You are given a text-only question on the subject of {quiz_name} in the image attached. Please carefully analyze the image and remember the content because it will be used in the following questions. You mustn't output any text in response to this question.
        YOU MUST NOT OUTPUT ANY TEXT OR SYMBOLS IN RESPONSE TO THIS QUESTION!
        """,

        'fill_in_multiple_blanks_question': f"""
        You are given a fill-in-multiple-blanks question on the subject of {quiz_name} in the image attached. Please carefully analyze the image and respond with ONLY the missing word(s) or numerical value(s) in the correct order, separated by spaces. For example, if the blanks are '___' and '___', and the correct answers are 'apple' and 'orange', respond with: 'apple orange'. Similarly, if the blanks require numerical values like '___' and '___' with answers '5' and '10', respond with: '5 10'. Do not provide any additional text, explanations, or reasoning—just the missing word(s) or numerical value(s) separated by spaces.
        Only the missing word(s) or numerical value(s) are required. Respond with the missing value(s) separated by spaces, nothing more.
        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        OUTPUT EXAMPLE: 'apple orange', '5 10', etc.
        """
    }
    return prompt_bank.get(question_type, "Invalid question type")
