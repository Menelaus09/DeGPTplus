# DeepSeek 模型配置指南

## 正确的模型名称

DeepSeek API 支持以下模型：

### 1. deepseek-chat（推荐）
- **用途**: 标准聊天和代码优化
- **特点**: 性能稳定，适合大多数任务
- **配置**:
```ini
[LLM]
model = deepseek-chat
api_key = your-api-key
api_base = https://api.deepseek.com/v1
temperature = 0.2
```

### 2. deepseek-reasoner（如果可用）
- **用途**: 需要复杂推理的任务
- **特点**: 更强的推理能力
- **配置**:
```ini
[LLM]
model = deepseek-reasoner
api_key = your-api-key
api_base = https://api.deepseek.com/v1
temperature = 0.2
```

## 常见错误

### ❌ 错误：deepseek-r1
```
Model Not Exist
```
**原因**: `deepseek-r1` 不是有效的模型名称

**解决**: 改为 `deepseek-chat`

### ❌ 错误：API Base 不匹配
如果使用 DeepSeek 模型，必须使用：
```
api_base = https://api.deepseek.com/v1
```

## 获取API密钥

1. 访问 https://platform.deepseek.com/
2. 注册/登录账户
3. 在控制台获取 API 密钥
4. 确保账户有足够余额

## 测试配置

运行测试脚本：
```bash
cd DeGPT/degpt
python test_api.py
```

## 完整配置示例

```ini
[LLM]
model = deepseek-chat
api_key = sk-your-deepseek-api-key-here
api_base = https://api.deepseek.com/v1
temperature = 0.2
```

## 注意事项

1. **模型名称区分大小写**: 使用 `deepseek-chat` 而不是 `DeepSeek-Chat`
2. **API密钥格式**: DeepSeek的API密钥通常以 `sk-` 开头
3. **API Base**: 必须使用 `https://api.deepseek.com/v1`
4. **余额检查**: 确保账户有足够余额

## 故障排查

如果仍然遇到 "Model Not Exist" 错误：

1. **检查模型名称**: 确认使用 `deepseek-chat`
2. **验证API密钥**: 确保密钥有效且未过期
3. **检查账户状态**: 登录平台确认账户正常
4. **查看API文档**: 访问 https://platform.deepseek.com/docs 查看最新模型列表


