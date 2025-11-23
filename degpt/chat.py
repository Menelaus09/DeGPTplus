"""
Interfaces to interact with various LLMs
"""

import json
import os
import atexit
import configparser
from typing import Dict, Optional, List
from openai import OpenAI


CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(CUR_DIR, 'config.ini')


def load_config(field: str, value: str) -> str:

    config = configparser.ConfigParser()
    # 使用UTF-8编码读取配置文件，避免中文注释导致的编码错误
    try:
        with open(CONFIG, 'r', encoding='utf-8') as f:
            config.read_file(f)
    except UnicodeDecodeError:
        # 如果UTF-8失败，尝试GBK（向后兼容）
        with open(CONFIG, 'r', encoding='gbk') as f:
            config.read_file(f)
    return config[field][value]


def llm_configured() -> bool:
    try:
        model = load_config('LLM', 'model')
        api_key = load_config('LLM', 'api_key')
        api_base = load_config('LLM', 'api_base')
        return bool(len(model) and len(api_key) and len(api_base))
    except (configparser.NoSectionError, configparser.NoOptionError, KeyError):
        return False


class QueryChatGPT():
    """ Interface for interacting with ChatGPT

    """

    def __init__(self) -> None:
        self.chat_context: List[Dict[str, str]] = []
        self.chat_history: List[Dict[str, str]] = []
        self.temperature:float = 0.2
        self.use_history = False
        self.system_prompt: Optional[str] = None
        atexit.register(self.log_history)

    def clear(self):
        self.chat_context = []

    def set_history(self, open: bool) -> None:
        self.use_history = open

    def insert_system_prompt(self, system_prompt: str) -> None:
        """ add system_prompt in self.chat_context """

        if self.chat_context and self.chat_context[0]["role"] == "system":
            self.chat_context[0]['content'] = system_prompt
        else:
            self.chat_context.insert(0, {
                "role": "system",
                "content": system_prompt
            })

    def log_history(self, log_file: str = 'chat_log.json'):

        if not os.path.exists(log_file):
            with open(log_file, 'w') as w:
                json.dump([], w, indent=4)

        with open(log_file, 'r') as r:
            log = json.load(r)
        assert (isinstance(log, list))
        log.append(self.chat_history)
        with open(log_file, 'w') as w:
            json.dump(log, w, indent=4)

    def __query(self, prompt: str, model: str) -> Optional[str]:
        self.chat_context.append({"role": "user", "content": prompt})
        self.chat_history.append({"role": "user", "content": prompt})

        try:
            api_key = load_config('LLM', 'api_key')
            api_base = load_config('LLM', 'api_base')
        except Exception as e:
            print(f"Error loading config: {e}")
            raise
        
        client = OpenAI(
            api_key=api_key, 
            base_url=api_base,
            timeout=120.0  # 增加超时时间到120秒，支持更强大的模型
        )
        
        # 对于更强大的模型，可以使用更高的temperature
        # 可以通过config.ini配置
        try:
            custom_temp = float(load_config('LLM', 'temperature'))
        except (configparser.NoOptionError, ValueError, KeyError):
            custom_temp = self.temperature
        
        try:
            response = client.chat.completions.create(
                messages=self.chat_context,  # type: ignore
                model=model,
                temperature=custom_temp,
            )
            response_content = str(response.choices[0].message.content)
        except Exception as e:
            error_msg = str(e)
            print(f"API调用失败:")
            print(f"  模型: {model}")
            print(f"  API Base: {api_base}")
            print(f"  API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
            print(f"  错误: {error_msg}")
            
            # 提供常见错误的解决建议
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                print("\n建议: API密钥可能无效或已过期，请检查:")
                print("  1. API密钥是否正确")
                print("  2. API密钥是否已激活")
                print("  3. API密钥是否有足够的余额")
            elif "404" in error_msg or "not found" in error_msg.lower():
                print("\n建议: 模型名称可能不正确，请检查:")
                print("  1. 模型名称是否正确")
                print("  2. API Base URL是否匹配模型提供商")
                print("  3. 如果使用DeepSeek，api_base应该是: https://api.deepseek.com/v1")
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                print("\n建议: 访问被拒绝，请检查:")
                print("  1. API密钥是否有权限访问该模型")
                print("  2. 账户是否有足够的配额")
            
            raise

        self.chat_context.append({
            "role": "assistant",
            "content": response_content
        })
        self.chat_history.append({
            "role": "assistant",
            "content": response_content
        })

        return response_content

    def query(self,
              prompt: str,
              *,
              model: Optional[str] = None) -> Optional[str]:
        # 延迟加载模型配置，避免模块导入时的编码错误
        if model is None:
            try:
                model = load_config('LLM', 'model')
            except (configparser.NoSectionError, configparser.NoOptionError, KeyError) as e:
                print(f"Error: Failed to load model from config: {e}")
                return None

        response = self.__query(prompt, model)
        if not self.use_history:
            self.clear()
        return response
