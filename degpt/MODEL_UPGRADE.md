# 模型升级和二角色机制说明

## 概述

本项目已升级支持**二角色机制**，并优化了对更强大AI模型的支持。

## 三角色 vs 二角色

### 三角色机制（原版）
- **Referee（裁判）**：分析代码，确定需要哪些优化
- **Advisor（顾问）**：提供具体的优化建议
- **Operator（操作员）**：执行优化并确保语义正确

**缺点**：需要多次API调用，效率较低，适合较弱的模型

### 二角色机制（新版，推荐）
- **Analyzer（分析器）**：分析代码，确定优化方向
- **Optimizer（优化器）**：直接进行优化，确保语义正确

**优点**：
- 更高效：减少API调用次数
- 更智能：利用强大模型的综合能力
- 更快速：一次调用完成多项优化

## 支持的模型

### 推荐使用（二角色模式）

#### 阿里云通义千问
- `qwen-max` - 最强模型，推荐用于二角色模式
- `qwen-plus` - 增强版，性能优秀
- `qwen-turbo` - 快速版本（当前默认）

#### OpenAI
- `gpt-4` - GPT-4 标准版
- `gpt-4-turbo` - GPT-4 Turbo，更快更强
- `gpt-3.5-turbo` - 经济型选择

#### Anthropic Claude
- `claude-3-opus` - 最强版本
- `claude-3-sonnet` - 平衡版本
- `claude-3-haiku` - 快速版本

## 配置方法

### 1. 修改 config.ini

编辑 `degpt/config.ini`：

```ini
[LLM]
model = qwen-max  # 改为更强大的模型
api_key = your-api-key
api_base = https://dashscope.aliyuncs.com/compatible-mode/v1
temperature = 0.2  # 可调整，0.0-1.0，值越高越有创造性
```

### 2. 使用二角色模式

#### 方法A：通过Web UI
1. 打开Web界面
2. 勾选"使用二角色模式"选项
3. 选择"全部优化"
4. 点击"开始优化"

#### 方法B：通过代码
```python
from role_v2 import dual_role_optimize

result = dual_role_optimize(decompile_code)
print(result['output'])
```

## 性能对比

| 模式 | API调用次数 | 适用模型 | 速度 | 质量 |
|------|------------|---------|------|------|
| 三角色 | 4-6次 | 较弱模型 | 慢 | 中等 |
| 二角色 | 2-3次 | 强大模型 | 快 | 高 |

## 注意事项

1. **模型选择**：二角色模式需要更强大的模型才能发挥优势
2. **API成本**：强大模型通常更贵，但调用次数更少
3. **超时设置**：已增加到120秒，支持更复杂的处理
4. **向后兼容**：仍支持三角色模式，可通过Web UI选择

## 故障排查

### 问题1：二角色模式不可用
- 确保 `role_v2.py` 文件存在
- 检查导入错误

### 问题2：优化质量不佳
- 尝试使用更强大的模型（如 qwen-max）
- 调整 temperature 参数
- 检查 prompt_v2.json 是否正确

### 问题3：超时错误
- 使用更快的模型（如 qwen-turbo）
- 减少代码长度
- 检查网络连接

## 示例配置

### 阿里云通义千问 Max（推荐）
```ini
[LLM]
model = qwen-max
api_key = your-dashscope-api-key
api_base = https://dashscope.aliyuncs.com/compatible-mode/v1
temperature = 0.2
```

### OpenAI GPT-4
```ini
[LLM]
model = gpt-4
api_key = your-openai-api-key
api_base = https://api.openai.com/v1
temperature = 0.2
```

### 本地模型（如Ollama）
```ini
[LLM]
model = llama2
api_key = ollama
api_base = http://localhost:11434/v1
temperature = 0.3
```

## 更新日志

- **v2.0**: 添加二角色机制支持
- **v2.0**: 增加超时时间到120秒
- **v2.0**: 支持自定义temperature配置
- **v2.0**: Web UI支持模式选择


