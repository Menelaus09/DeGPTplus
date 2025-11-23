"""
测试API配置和连接
"""
import sys
import os

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from chat import load_config, llm_configured, QueryChatGPT

def test_config():
    """测试配置读取"""
    print("=" * 50)
    print("测试配置读取")
    print("=" * 50)
    
    try:
        model = load_config('LLM', 'model')
        api_key = load_config('LLM', 'api_key')
        api_base = load_config('LLM', 'api_base')
        
        print(f"✓ 模型: {model}")
        print(f"✓ API Base: {api_base}")
        print(f"✓ API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
        
        # 检查配置是否匹配
        print("\n配置检查:")
        if "deepseek" in model.lower():
            if "dashscope" in api_base.lower():
                print("⚠ 警告: 检测到DeepSeek模型，但API Base指向DashScope")
                print("   建议: 如果使用DeepSeek，api_base应该是: https://api.deepseek.com/v1")
            elif "deepseek" not in api_base.lower():
                print("⚠ 警告: DeepSeek模型可能需要特定的API Base")
        elif "qwen" in model.lower():
            if "dashscope" not in api_base.lower():
                print("⚠ 警告: Qwen模型通常需要DashScope的API Base")
        
        return True
    except Exception as e:
        print(f"✗ 配置读取失败: {e}")
        return False

def test_api_connection():
    """测试API连接"""
    print("\n" + "=" * 50)
    print("测试API连接")
    print("=" * 50)
    
    if not llm_configured():
        print("✗ LLM未配置")
        return False
    
    try:
        q = QueryChatGPT()
        q.insert_system_prompt("You are a helpful assistant.")
        
        # 发送一个简单的测试请求
        print("发送测试请求...")
        response = q.query("Say 'Hello' in one word.")
        
        if response:
            print(f"✓ API调用成功!")
            print(f"  响应: {response[:100]}...")
            return True
        else:
            print("✗ API调用返回空响应")
            return False
            
    except Exception as e:
        print(f"✗ API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("DeGPT API 配置测试工具\n")
    
    config_ok = test_config()
    if not config_ok:
        print("\n请先修复配置问题")
        sys.exit(1)
    
    print("\n")
    api_ok = test_api_connection()
    
    if api_ok:
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！API配置正确")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("✗ API测试失败，请检查配置")
        print("=" * 50)
        sys.exit(1)


