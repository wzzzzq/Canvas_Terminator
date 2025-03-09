import openai
import os
import httpx
import base64

no_proxy_client = httpx.Client(transport=httpx.HTTPTransport(proxy=None))

class GPTClientBase:
    def __init__(self, *args):
        self.key, self.model, self.url, self.provider = args[0], args[1], args[2], args[3] if len(args) > 3 else None
        self.client = openai.OpenAI(api_key=self.key, base_url=self.url, http_client=no_proxy_client)
        self.content = None
        self.conversation_history = []

    def send_text(self, msg, max_tokens=None):
        attempts = 0
        while attempts < 5:
            try:
                params = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": msg}]
                }
                if max_tokens:
                    params["max_tokens"] = max_tokens
                    
                self.content = self.client.chat.completions.create(**params)
                return self.get_response()
            except Exception as e:
                attempts += 1
                if attempts >= 5:
                    raise e

    def send_messages(self, conv, max_tokens=None):
        attempts = 0
        while attempts < 5:
            try:
                params = {
                    "model": self.model,
                    "messages": conv
                }
                if max_tokens:
                    params["max_tokens"] = max_tokens
                    
                self.content = self.client.chat.completions.create(**params)
                return self.get_response()
            except Exception as e:
                attempts += 1
                if attempts >= 5:
                    raise e

    def get_response(self):
        return self.content.choices[0].message.content if self.content else None
    
    def send_image(self, text, image_path, max_tokens=None):
        """Send text and image to the model and get response.
        
        Args:
            text (str): The text prompt to send
            image_path (str): Path to the image file
            max_tokens (int, optional): Maximum number of tokens in response
        
        Returns:
            str: Model's response or None if failed
        """
        attempts = 0
        while attempts < 5:
            try:
                # Read and encode image
                with open(image_path, 'rb') as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Create message with text and image
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": text
                            }
                        ]
                    }
                ]
                
                # Send to API with optional max_tokens
                params = {
                    "model": self.model,
                    "messages": messages
                }
                if max_tokens:
                    params["max_tokens"] = max_tokens
                    
                self.content = self.client.chat.completions.create(**params)
                return self.get_response()
                
            except Exception as e:
                attempts += 1
                if attempts >= 5:
                    print(f"Failed to process image after {attempts} attempts: {str(e)}")
                    raise e

    def send_image_with_history(self, text, image_path, max_tokens=None):
        """Send text and image while maintaining conversation history.
        
        Args:
            text (str): The text prompt to send
            image_path (str): Path to the image file
            max_tokens (int, optional): Maximum number of tokens in response
        
        Returns:
            str: Model's response or None if failed
        """
        attempts = 0
        while attempts < 5:
            try:
                # Read and encode image
                with open(image_path, 'rb') as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Create new message
                new_message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
                
                # Add new message to history
                self.conversation_history.append(new_message)
                
                # Send to API with history
                params = {
                    "model": self.model,
                    "messages": self.conversation_history
                }
                if max_tokens:
                    params["max_tokens"] = max_tokens
                
                self.content = self.client.chat.completions.create(**params)
                response = self.get_response()
                
                # Add assistant's response to history
                if response:
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response
                    })
                
                return response
                
            except Exception as e:
                attempts += 1
                if attempts >= 5:
                    print(f"Failed to process image after {attempts} attempts: {str(e)}")
                    raise e
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []

from dotenv import load_dotenv
load_dotenv()

GLM1 = GPTClientBase(os.getenv("GLM_API_KEY"), "glm-4-plus", "https://open.bigmodel.cn/api/paas/v4/", "智谱")
GLM2 = GPTClientBase(os.getenv("GLM_API_KEY"), "glm-4v-plus", "https://open.bigmodel.cn/api/paas/v4/", "智谱")
DOUBAO1 = GPTClientBase(os.getenv("ARK_API_KEY"), "doubao-1-5-vision-pro-32k-250115", "https://ark.cn-beijing.volces.com/api/v3", "ByteDance")
DOUBAO2 = GPTClientBase(os.getenv("ARK_API_KEY"), "doubao-vision-pro-32k-241028", "https://ark.cn-beijing.volces.com/api/v3", "ByteDance")
DOUBAO3 = GPTClientBase(os.getenv("ARK_API_KEY"), "doubao-1-5-pro-256k-250115", "https://ark.cn-beijing.volces.com/api/v3", "ByteDance")
DeepSeek = GPTClientBase(os.getenv("ARK_API_KEY"), "deepseek-r1-250120", "https://ark.cn-beijing.volces.com/api/v3", "DeepSeek")

def get_gpt_clients() -> list:
    return [
        ("GLM-4V", GLM2),
        ("DOUBAO-1.5V", DOUBAO1),
        ("DOUBAO-V-PRO", DOUBAO2),
        ("DOUBAO-1.5-PRO", DOUBAO3),
        ("GLM-4+", GLM1),
        ("DeepSeek", DeepSeek),
    ]

def get_gpt_client_dict() -> dict:
    clients = get_gpt_clients()
    return {client[0]: client[1] for client in clients}

if __name__ == "__main__":
    client_dict = get_gpt_client_dict()
    model = "GLM-4"
    client = client_dict[model]
    response = client.send_image("tell me the answer of the question in the image","/home/christianwang/Downloads/test.jpg",max_tokens=512)
    print(response)
