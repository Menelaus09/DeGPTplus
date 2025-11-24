# 故障排查指南

## 超时问题

如果遇到 "Request timed out" 或 "连接超时" 错误，请尝试以下解决方案：

### 1. 检查网络连接
- 确保网络连接稳定
- 检查是否能正常访问互联网
- 如果使用代理，确保代理配置正确

### 2. 检查API配置
- 确认 `degpt/config.ini` 中的API配置正确
- 验证API密钥是否有效
- 确认API服务器地址可访问

### 3. 减少代码长度
- 如果代码过长，尝试分段处理
- 先优化较小的代码片段
- 避免一次性处理过大的代码

### 4. 增加超时时间（高级）

如果需要增加超时时间，可以修改 `degpt/chat.py` 文件：

在 `__query` 方法中，修改 OpenAI 客户端创建部分：

```python
from openai import OpenAI
import httpx

client = OpenAI(
    api_key=load_config('LLM', 'api_key'), 
    base_url=load_config('LLM', 'api_base'),
    timeout=httpx.Timeout(60.0, connect=30.0)  # 增加超时时间
)
```

### 5. 检查防火墙和代理
- 确保防火墙允许Python访问网络
- 如果使用企业代理，可能需要配置代理设置
- 检查是否有VPN影响连接

### 6. 重试
- 网络问题可能是暂时的，稍后重试
- 使用界面上的"重试"按钮

## 其他常见问题

### 模块未找到
如果提示 `ModuleNotFoundError`，请运行：
```bash
pip install -r requirements.txt
```

### 配置未完成
确保 `degpt/config.ini` 文件已正确配置：
```ini
[LLM]
model = your-model-name
api_key = your-api-key
api_base = your-api-base-url
```

### 端口被占用
如果5000端口被占用，可以修改 `app.py` 最后一行：
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为其他端口
```





