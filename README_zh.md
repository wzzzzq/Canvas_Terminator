# 基于Selenium和LLM大模型的交大canvas解题助手

一款使用Selenium WebDriver和基于GPT的AI模型自动解答Canvas测验的工具。

*其他语言版本: [English](README.md), [简体中文](README_zh.md)*

## 免责声明

**注意：实际使用时请确保遵守学校教学管理规定，本工具仅用于技术研究目的。部分功能需要配合合法的API服务使用，请自行申请相关接口权限。**

## 功能特点

- 自动登录Canvas系统（含验证码识别）
- 查找并导航至特定课程和测验
- 支持多种题型：
  - 单选题
  - 多选题
  - 数值题
  - 多空填空题
- 本地保存答案以便将来使用
- 重复测验时可重用之前的答案
- 对题目截图或提取以进行AI处理
- 基于GPT的答案生成

## 系统要求

- Python 3.8+
- Chrome浏览器
- Tesseract（用于登录时的验证码识别）

    Ubuntu用户可使用以下命令安装：
    ```bash
    sudo apt-get install tesseract-ocr
    ```

## 安装方法

1. 克隆仓库：
    ```bash
    git clone https://github.com/yourusername/Auto_Canvas_Quiz.git
    cd Auto_Canvas_Quiz
    ```

2. （可选）创建虚拟环境：
    ```bash
    conda create -n canvas python=3.10
    conda activate canvas
    ```

3. 安装所需软件包：
    ```bash
    pip install -r requirements.txt
    ```

4. 设置环境变量：
    在config.py根据注释设置账号密码，AI工具的API key，以及解题模型

    本项目目前默认使用火山引擎的豆包和deepseek，以及GLM模型

## 使用方法

1. 运行主脚本：
    ```bash
    python main.py
    ```

2. 脚本将会：
   - 自动登录Canvas
   - 导航到指定课程
   - AI模式：
   
        - 查找可用测验
        - 对问题截图
        - 使用AI生成答案
        - 提交答案
        - 保存答案以供将来使用
        
    - 已保存答案模式（仅在有本地答案时可见）：
   
        - 加载本地答案 （从correct_answer文件夹）
        - 提交答案

## 项目结构

```
Canvas_Terminator/
├── main.py             # 主入口
├── solve.py            # 测验解答逻辑
├── canvas.py           # Canvas交互函数
├── webdriver.py        # Selenium WebDriver设置
├── gpt_client_bank.py  # GPT客户端实现
├── prompt_bank.py      # 不同问题的AI提示
├── config.py           # 配置文件
├── screenshots/        # 问题截图
├── answers/            # 保存的测验答案
└── utils/              # 工具函数
```

## 配置

- 问题截图保存在 `screenshots/<quiz_name>/` 目录下
- 答案以JSON格式保存在 `answers/<quiz_name>.json` 文件中
- GPT提示可以在 `prompt_bank.py` 中自定义
## 答案格式

答案以JSON格式保存：
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

## 注意事项

- 工具会尊重测验的可用性和尝试限制
- 答案可以用于多次尝试
- 截图保存以供验证
- 控制台输出提供详细的进度信息
