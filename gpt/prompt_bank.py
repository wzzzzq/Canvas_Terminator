def get_prompt_text(quiz_name, question_type, question, options):
    options_str = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])
    
    prompt_bank = {
        'multiple_choice_question': f"{quiz_name} quiz question:\n\n"
                                   f"QUESTION: {question}\n"
                                   f"OPTIONS:\n{options_str}\n\n"
                                   f"RESPOND ONLY WITH ONE LETTER (A-{chr(64+len(options))}).\n"
                                   f"DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!\n"
                                   f"Example: A",

        'multiple_answers_question': f"{quiz_name} quiz question:\n\n"
                                    f"QUESTION: {question}\n"
                                    f"OPTIONS:\n{options_str}\n\n"
                                    f"RESPOND ONLY WITH LETTERS OF ALL CORRECT OPTIONS (no separators).\n"
                                    f"DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!\n"
                                    f"Example: AB or ACD",
                
        'numerical_question': f"{quiz_name} quiz question:\n\n"
                             f"QUESTION: {question}\n\n"
                             f"RESPOND ONLY WITH THE NUMERICAL VALUE. NO UNITS OR SPECIAL CHARACTERS.\n"
                             f"DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!\n"
                             f"Example: 3 or 4.2",

        'text_only_question': f"Context information for upcoming questions:\n\n"
                             f"CONTENT: {question}\n\n"
                             f"STORE THIS INFORMATION BUT DO NOT OUTPUT ANY TEXT.",

        'fill_in_multiple_blanks_question': f"{quiz_name} quiz question:\n\n"
                                          f"QUESTION: {question}\n\n"
                                          f"RESPOND ONLY WITH SPACE-SEPARATED VALUES FOR EACH BLANK.\n"
                                          f"DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!\n"
                                          f"Example: word1 word2"
    }
    return prompt_bank.get(question_type, "Invalid question type")


def get_prompt_image(quiz_name, question_type):
    prompt_bank = {
        'multiple_choice_question': f"{quiz_name} quiz (image question):\n\n"
                                   f"RESPOND ONLY WITH ONE LETTER (A-Z) FOR THE CORRECT ANSWER.\n"
                                   f"DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!\n"
                                   f"Example: A",

        'multiple_answers_question': f"{quiz_name} quiz (image question):\n\n"
                                    f"RESPOND ONLY WITH LETTERS OF ALL CORRECT OPTIONS (no separators).\n"
                                    f"DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!\n"
                                    f"Example: AB or ACD",
        
        'numerical_question': f"{quiz_name} quiz (image question):\n\n"
                             f"RESPOND ONLY WITH THE NUMERICAL VALUE. NO UNITS.\n"
                             f"DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!\n"
                             f"Example: 3 or 4.2",

        'text_only_question': f"Context information for upcoming questions (image):\n\n"
                             f"STORE THIS INFORMATION BUT DO NOT OUTPUT ANY TEXT.",

        'fill_in_multiple_blanks_question': f"{quiz_name} quiz (image question):\n\n"
                                          f"RESPOND ONLY WITH SPACE-SEPARATED VALUES FOR EACH BLANK.\n"
                                          f"DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!\n"
                                          f"Example: word1 word2"
    }
    return prompt_bank.get(question_type, "Invalid question type")


def get_feedback_prompt(question, wrong_answer):
    feedback = f"Question: {question}\n\n"
    feedback += f"Here are the previous wrong answers:\n"
    
    for ans, score in wrong_answer:
        feedback += f"- {ans} (score: {score})\n"
        
    feedback += f"\nRESPOND ONLY WITH THE CORRECT ANSWER  DIFFERENT FROM THE WRONG ANSWERS. DO NOT PROVIDE ANY EXPLANATIONS OR REASONING!"
    return feedback
