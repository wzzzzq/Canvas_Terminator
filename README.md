# Canvas_Terminator

An automated tool to solve Canvas quizzes using Selenium WebDriver and GPT-based AI models.

## Disclaimer

**Note: Please ensure compliance with your school's academic policies when using this tool. It is intended for research purposes only. Some features require legitimate API services, so please apply for the necessary permissions.**


**注意：实际使用时请确保遵守学校教学管理规定，本工具仅用于技术研究目的。部分功能需要配合合法的API服务使用，请自行申请相关接口权限。**


## Features

- Automatic login to Canvas with captcha recognition
- Find and navigate to specific courses and quizzes
- Support multiple question types:
  - Multiple choice questions
  - Multiple answer questions
  - Numerical questions
  - Fill in multiple blanks questions
- Save quiz answers locally for future attempts
- Reuse previous answers when retaking quizzes
- Screenshot questions for AI processing
- GPT-based answer generation

## Prerequisites

- Python 3.8+
- Chrome browser
- JAccount credentials for SJTU Canvas
- Tesseract (Used to recognize the captcha when logging in)

    For Ubuntu Users, you can use the following command:
    ````bash
    sudo apt-get install tesseract-ocr
    ````

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Auto_Canvas_Quiz.git
cd Auto_Canvas_Quiz
```

2. (Optional) Create Virtual Environment
````bash
conda create -n canvas python=3.10
conda activate canvas
````

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
touch .env

# Add your credentials and API keys
GLM_API_KEY=your_glm_api_key
JACCOUNT_USERNAME=your_jaccount
JACCOUNT_PASSWORD=your_password
```

## Usage

1. Run the main script:
```bash
python main.py
```

2. The script will:
   - Login to Canvas automatically
   - Navigate to specified course
    AI mode:
        - Find available quizzes
        - Take screenshots of questions
        - Generate answers using AI
        - Submit responses
        - Save answers for future use
    Saved Answer mode (only visible when there is local answer):
        - load local answers
        - Submit responses

## Project Structure

```
Canvas_Terminator/
├── main.py             # Main entry point
├── solve.py            # Quiz solving logic
├── canvas.py           # Canvas interaction functions
├── webdriver.py        # Selenium WebDriver setup
├── gpt_client_bank.py  # GPT client implementations
├── prompt_bank.py      # AI prompts for different questions
├── config.py           # Configurations
├── screenshots/        # Question screenshots
├── answers/            # Saved quiz answers
└── utils/              # Utility functions
```

## Configuration

- Questions are saved as screenshots in `screenshots/<quiz_name>/`
- Answers are saved as JSON in `answers/<quiz_name>.json`
- GPT prompts can be customized in `prompt_bank.py`

## Answer Format

Answers are saved in JSON format:
```json
{
  "quiz_name": "Quiz 1",
  "timestamp": "2025-03-08T14:30:00.123456",
  "answers": {
    "1": {
      "type": "multiple_choice_question",
      "response": "B",
      "value": ["2412"]
    },
    "2": {
      "type": "multiple_answers_question",
      "response": "ABC",
      "value": ["1234", "5678", "9012"]
    }
  }
}
```

## Notes

- The tool respects quiz availability and attempt limits
- Answers can be reused for multiple attempts
- Screenshots are saved for verification
- Console output provides detailed progress information