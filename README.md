# Canvas_Terminator

An automated tool to solve Canvas quizzes using Selenium WebDriver and GPT-based AI models.

## Disclaimer

**Note: Please ensure compliance with your school's academic policies when using this tool. It is intended for research purposes only. Some features require legitimate API services, so please apply for the necessary permissions.**


**注意：实际使用时请确保遵守学校教学管理规定，本工具仅用于技术研究目的。部分功能需要配合合法的API服务使用，请自行申请相关接口权限。**

## 快速上手指南
本项目还处于内测阶段，目前支持的功能包括自动登陆交大canvas，检测可以尝试无限次尝试的测验，根据用户的选择决定使用本地保存的答案，或者使用AI一键完成。

使用之前请确保你的电脑安装了python，接着需要安装一些依赖的软件和包。然后在项目文件夹里新建一个.env文件写入你的jaccount账号密码，就可以运行程序了。（具体请往下阅读）

如果你想使用AI接入功能，则需要多申请一个api key. 这里默认地是使用[智谱清言](https://bigmodel.cn/)的API，新用户注册会送2000万tokens，基本够用了。注册完成后创建一个api key，加入到.env文件中，就可以解锁AI功能了！

另外，安装教程是以Linux系统写的，Windows操作会略有一点点不同，以后会完善教程。

目前存在的问题
- AI 回答准确度有时候不高。目前的回答策略是一次性答完所有题目，后续可能推出例如一道一道做直到答对。
- 目前的函数都是默认测验不会显示正确答案来做的，如果一次测验后会显示正确答案就很简单了，不过目前还没做这个功能。

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
   - AI mode:
   
        - Find available quizzes
        - Take screenshots of questions
        - Generate answers using AI
        - Submit responses
        - Save answers for future use
        
    - Saved Answer mode (only visible when there is local answer):
   
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
