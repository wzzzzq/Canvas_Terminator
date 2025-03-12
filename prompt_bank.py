def get_prompt_text(quiz_name, question_type, question, options):
    options_str = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])
    
    prompt_bank = {
        'multiple_choice_question': f"""
        The following is a Multiple Choice Question on the subject of {quiz_name}

        QUESTION: {question}
        OPTIONS:
        {options_str}

        Only the letter of the correct answer is required. Respond with 'A', 'B', 'C', 'D', etc., nothing more.
        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        YOU MUST RESPOND WITH ONLY THE LETTER OF THE CORRECT ANSWER WITHOUT ANY ADDITIONAL TEXT OR SYMBOLS!!!
        OUTPUT EXAMPLE: 'A', 'B', 'C', 'D', etc.
        """,

        'multiple_answers_question': f"""
        The following is a Multiple Answers Question on the subject of {quiz_name}

        QUESTION: {question}
        OPTIONS:
        {options_str}

        Only the concatenated letters of the correct answers in alphabetical order are required. Respond with a minimum of 1 and a maximum of {len(options)} letters. No separators between letters.

        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        YOU MUST RESPOND WITH ONLY THE LETTERS OF THE CORRECT ANSWERS WITHOUT ANY ADDITIONAL TEXT OR SYMBOLS!!!
        OUTPUT EXAMPLE: 'AB', 'ACD', 'BCE'
        """,
                
        'numerical_question': f"""
        The following is a Numerical Question on the subject of {quiz_name}

        QUESTION: {question}

        Only the numerical value is required. Respond with integers, decimals, or scientific notation. No units, symbols, or Chinese characters. Maximum 6 significant figures.

        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        YOU MUST RESPOND WITH ONLY THE NUMERICAL VALUE WITHOUT ANY ADDITIONAL TEXT OR SYMBOLS!!!
        OUTPUT EXAMPLE: '3', '4.2'
        """,

        'text_only_question': f"""
        The following is a piece of context which may be useful in the following questions
        CONTENT: {question}

        No output is required. Store the context for future questions.

        DO NOT OUTPUT ANYTHING!
        EXPECTED OUTPUT: [EMPTY STRING]
        """,

        'fill_in_multiple_blanks_question': f"""
        The following is a Fill-in-Blanks Question on the subject of {quiz_name}

        QUESTION TEMPLATE: {question}
        (Example input: "_ discovered _", output: "Watson Crick")

        Only the space-separated values are required. Preserve original case. No numbering or prefixes.

        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        YOU MUST RESPOND WITH ONLY THE SPACE-SEPARATED VALUES WITHOUT ANY ADDITIONAL TEXT OR SYMBOLS!!!
        OUTPUT EXAMPLE: 'DNA', '5 3.14', 'ATP synthase'
        """
    }
    return prompt_bank.get(question_type, "Invalid question type")


def get_prompt_image(quiz_name, question_type):
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
        OUTPUT ONLY A NUMERICAL VALUE! Respond with '1', '2', '3', etc., nothing more.
        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        OUTPUT EXAMPLE: '1', '2.4', '3', etc.
        """,

        'text_only_question': f"""
        You are given a piece of context on the subject of {quiz_name} in the image attached. Please carefully analyze the image and remember the content because it will be used in the following questions. You mustn't output any text in response to this question.
        YOU MUST NOT OUTPUT ANY TEXT OR SYMBOLS IN RESPONSE TO THIS QUESTION!
        """,

        'fill_in_multiple_blanks_question': f"""
        You are given a fill-in-multiple-blanks question on the subject of {quiz_name} in the image attached. Please carefully analyze the image and respond with ONLY the missing word(s) or numerical value(s) in the correct order, separated by spaces. For example, if the blanks are '___' and '___', and the correct answers are 'apple' and 'orange', respond with: 'apple orange'. Similarly, if the blanks require numerical values like '___' and '___' with answers '5' and '10', respond with: '5 10'. Do not provide any additional text, explanations, or reasoning—just the missing word(s) or numerical value(s) separated by spaces.
        Only the missing word(s) or numerical value(s) are required. Respond with the missing value(s) separated by spaces, nothing more.
        DO NOT OUTPUT ANY ADDITIONAL TEXT, EXPLANATIONS, OR REASONING!
        THE ANSWERS SHOULD BE SEPERATED BY SPACE ONLY!
        OUTPUT EXAMPLE: 'apple orange', '5 10', etc.
        """
    }
    return prompt_bank.get(question_type, "Invalid question type")

def get_feedback_prompt(wrong_answer):
    feedback_prompt = f"""Your answer is incorrect. Pleae try again. Make sure to output only the correct answer according to the previous instructions without any additional text or symbols.
    Known wrong answers: {wrong_answer}"""
    return feedback_prompt