from config import language

# Translation dictionary
translations = {
    # Main program messages
    "welcome": {
        "en": "Welcome to the Canvas Quiz Solver!",
        "zh": "欢迎使用Canvas测验解答工具！"
    },
    "found_quizzes": {
        "en": "Found {0} available quizzes:",
        "zh": "找到{0}个可用的测验："
    },
    "processing_quiz": {
        "en": "Processing quiz: {0}",
        "zh": "正在处理测验：{0}"
    },
    "use_saved": {
        "en": "Use saved answers",
        "zh": "使用已保存的答案"
    },
    "solve_auto": {
        "en": "Solve with AI (auto mode)",
        "zh": "使用AI自动解答"
    },
    "solve_image": {
        "en": "Solve with AI (image mode)",
        "zh": "使用AI图像模式解答"
    },
    "solve_verify": {
        "en": "Solve one by one (verify each answer)",
        "zh": "逐一解答（验证每个答案）"
    },
    "skip_quiz": {
        "en": "Skip this quiz",
        "zh": "跳过此测验"
    },
    "exit_program": {
        "en": "Exit program",
        "zh": "退出程序"
    },
    "invalid_choice": {
        "en": "Invalid choice. Please try again.",
        "zh": "无效选择。请重试。"
    },
    "exiting": {
        "en": "Exiting program...",
        "zh": "正在退出程序..."
    },
    "enter_choice_saved": {
        "en": "Enter your choice (1-6): ",
        "zh": "输入您的选择（1-6）："
    },
    "enter_choice_no_saved": {
        "en": "Enter your choice (1-5): ",
        "zh": "输入您的选择（1-5）："
    },
    "loading_answers": {
        "en": "Loading saved answers for {0}...",
        "zh": "正在加载{0}的已保存答案..."
    },
    "solving_auto": {
        "en": "Solving {0} with AI in auto mode...",
        "zh": "使用AI自动模式解答{0}..."
    },
    "solving_image": {
        "en": "Solving {0} with AI in image mode...",
        "zh": "使用AI图像模式解答{0}..."
    },
    "solving_verify": {
        "en": "Solving {0} one by one, verifying each answer...",
        "zh": "逐一解答{0}，验证每个答案..."
    },
    "skipping": {
        "en": "Skipping {0}",
        "zh": "跳过{0}"
    },
    "no_quizzes": {
        "en": "No available quizzes found matching '{0}'",
        "zh": "未找到符合'{0}'的可用测验"
    },
    
    # Solve.py messages
    "retrying_question": {
        "en": "Retrying question {0}, attempt {1}",
        "zh": "重试问题{0}，尝试次数{1}"
    },
    "submitting": {
        "en": "Submitting quiz...",
        "zh": "正在提交测验..."
    },
    "correct": {
        "en": "✓ CORRECT! Got {0} points",
        "zh": "✓ 正确！获得{0}分"
    },
    "incorrect": {
        "en": "✗ INCORRECT. Got {0} out of {1} points",
        "zh": "✗ 错误。获得{0}/{1}分"
    },
    "max_attempts": {
        "en": "Max attempts reached for question {0}",
        "zh": "问题{0}已达到最大尝试次数"
    },
    "question_header": {
        "en": "----- Question {0} ({1} pts) -----",
        "zh": "----- 问题{0}（{1}分）-----"
    },
    "already_correct": {
        "en": "Already have correct answer for question {0}, skipping",
        "zh": "已有问题{0}的正确答案，跳过"
    },
    "vision_model_info": {
        "en": "Using vision model: {0}",
        "zh": "使用视觉模型：{0}"
    },
    "loaded_answers": {
        "en": "Loaded {0} existing correct answers",
        "zh": "已加载{0}个现有正确答案"
    }
}

def get_text(key, *args):
    """
    Get translated text for the given key and format with args
    """
    # Default to English if language not found
    current_lang = language if language in ["en", "zh"] else "en"
    
    if key not in translations:
        # Return the key itself if translation not found
        return key
    
    if current_lang not in translations[key]:
        # Fall back to English if specific language translation not found
        current_lang = "en"
    
    # Get and format the text
    text = translations[key][current_lang]
    if args:
        try:
            return text.format(*args)
        except:
            return text
    return text
