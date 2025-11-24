"""
Interfaces to interact with various LLMs
"""

import json
import os
import atexit
import configparser
from typing import Dict, Optional, List, Tuple
from openai import OpenAI
import httpx


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


def test_llm_connection() -> Tuple[bool, str]:
    """
    在启动 Web 服务时用于快速检测 LLM API 连接是否正常。
    返回 (是否成功, 中文说明信息)。
    """
    try:
        model = load_config('LLM', 'model')
        api_key = load_config('LLM', 'api_key')
        api_base = load_config('LLM', 'api_base')
    except Exception as e:
        return False, f"读取 config.ini 配置失败：{e}"

    try:
        # 使用 models.list 进行轻量级连通性与鉴权检查，不消耗推理 Token
        http_client = httpx.Client(timeout=15.0)
        client = OpenAI(
            api_key=api_key,
            base_url=api_base,
            http_client=http_client,
        )
        _ = client.models.list()
        return True, f"成功连接到 LLM API，当前模型：{model}"
    except Exception as e:
        error_msg = str(e)
        friendly = "LLM API 连接失败。\n"

        msg_lower = error_msg.lower()
        if "401" in error_msg or "unauthorized" in msg_lower:
            friendly += (
                "可能原因：\n"
                "- API 密钥无效或已过期；\n"
                "- 账户没有访问当前模型的权限。\n"
                "请检查 config.ini 中 [LLM] 部分的 api_key 配置。\n"
            )
        elif "404" in error_msg or "not found" in msg_lower:
            friendly += (
                "可能原因：\n"
                "- 模型名称填写错误；\n"
                "- api_base 与实际服务提供方不匹配。\n"
                "请检查 config.ini 中 model 与 api_base 是否对应正确。\n"
            )
        elif "timeout" in msg_lower:
            friendly += (
                "可能原因：\n"
                "- 网络不稳定或延迟过高；\n"
                "- 目标服务暂时不可用。\n"
                "建议：检查本机网络，稍后重试。\n"
            )
        elif "connection" in msg_lower or "connect" in msg_lower:
            friendly += (
                "可能原因：\n"
                "- 无法连接到 API 服务器；\n"
                "- 代理、防火墙或公司网络策略阻断了外网访问。\n"
                "建议：\n"
                "- 在浏览器中访问 api_base 所指向的域名测试连通性；\n"
                "- 检查代理 / VPN / 防火墙设置。\n"
            )
        else:
            friendly += f"原始错误信息：{error_msg}\n"

        return False, friendly


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
        
        # 创建 httpx 客户端，不传递 proxies 参数，避免版本兼容性问题
        http_client = httpx.Client(timeout=120.0)
        
        client = OpenAI(
            api_key=api_key, 
            base_url=api_base,
            http_client=http_client
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
