# API调用问题排查指南

## 常见问题

### 问题1：API密钥无效 (401 Unauthorized)

**症状**：
- 错误信息包含 "401" 或 "unauthorized"
- "Invalid API key"

**解决方案**：
1. 检查API密钥是否正确复制（注意前后空格）
2. 确认API密钥已激活
3. 检查账户余额是否充足
4. 验证API密钥是否属于正确的服务提供商

### 问题2：模型不存在 (404 Not Found)

**症状**：
- 错误信息包含 "404" 或 "model not found"
- "The model does not exist"

**可能原因**：
- 模型名称拼写错误
- API Base URL与模型提供商不匹配
- 模型在当前区域不可用

**解决方案**：

#### DeepSeek模型
```ini
[LLM]
model = deepseek-r1
api_key = your-deepseek-api-key
api_base = https://api.deepseek.com/v1
temperature = 0.2
```

#### 阿里云通义千问
```ini
[LLM]
model = qwen-max
api_key = your-dashscope-api-key
api_base = https://dashscope.aliyuncs.com/compatible-mode/v1
temperature = 0.2
```

#### OpenAI
```ini
[LLM]
model = gpt-4
api_key = your-openai-api-key
api_base = https://api.openai.com/v1
temperature = 0.2
```

### 问题3：访问被拒绝 (403 Forbidden)

**症状**：
- 错误信息包含 "403" 或 "forbidden"
- "Access denied"

**解决方案**：
1. 检查API密钥是否有权限访问该模型
2. 确认账户有足够的配额
3. 检查是否启用了该模型服务

### 问题4：配置不匹配

**症状**：
- 模型名称与API Base不匹配
- 例如：DeepSeek模型使用DashScope的API Base

**解决方案**：
确保模型名称、API密钥和API Base来自同一个服务提供商：

| 模型提供商 | 模型示例 | API Base |
|----------|---------|----------|
| DeepSeek | deepseek-r1, deepseek-chat | https://api.deepseek.com/v1 |
| 阿里云DashScope | qwen-max, qwen-plus, qwen-turbo | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| OpenAI | gpt-4, gpt-3.5-turbo | https://api.openai.com/v1 |
| Anthropic | claude-3-opus | https://api.anthropic.com/v1 |

## 测试工具

运行测试脚本检查配置：

```bash
cd DeGPT/degpt
python test_api.py
```

这个脚本会：
1. 检查配置文件是否正确读取
2. 验证配置是否匹配
3. 测试API连接
4. 提供详细的错误信息

## 配置检查清单

- [ ] API密钥格式正确（没有多余空格）
- [ ] API密钥已激活
- [ ] 账户有足够余额
- [ ] 模型名称正确
- [ ] API Base URL与模型提供商匹配
- [ ] 网络连接正常
- [ ] 防火墙/代理设置正确

## 快速修复

### DeepSeek配置示例
```ini
[LLM]
model = deepseek-r1
api_key = sk-your-deepseek-api-key-here
api_base = https://api.deepseek.com/v1
temperature = 0.2
```

### 获取API密钥

- **DeepSeek**: https://platform.deepseek.com/
- **阿里云DashScope**: https://dashscope.aliyun.com/
- **OpenAI**: https://platform.openai.com/
- **Anthropic**: https://console.anthropic.com/

## 调试步骤

1. **运行测试脚本**
   ```bash
   python test_api.py
   ```

2. **检查错误信息**
   - 查看完整的错误堆栈
   - 注意错误代码（401, 403, 404等）

3. **验证配置**
   - 确认config.ini格式正确
   - 检查是否有编码问题

4. **测试网络连接**
   - 确认可以访问API服务器
   - 检查防火墙设置

5. **联系支持**
   - 如果问题持续，联系API服务提供商支持


