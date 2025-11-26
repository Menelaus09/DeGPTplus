# DeGPT 快速参考

## 🚀 一键安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 cinspector
git clone https://github.com/PeiweiHu/cinspector
cd cinspector && pip install . && cd ..

# 3. 配置 API（编辑 degpt/config.ini）
# 填入您的 api_key
```

## 📝 配置 API

编辑 `degpt/config.ini`：

```ini
[LLM]
model = qwen-turbo
api_key = YOUR_API_KEY_HERE
api_base = https://dashscope.aliyuncs.com/compatible-mode/v1
```

## ▶️ 运行命令

### 命令行模式

```bash
# 基本用法
python degpt/role.py -f <输入文件> <输出名称>

# 示例
python degpt/role.py -f testcase/fibon out.json

# 指定优化类型
python degpt/role.py -f testcase/fibon out.json -t all      # 全部优化
python degpt/role.py -f testcase/fibon out.json -t simplify # 仅简化
python degpt/role.py -f testcase/fibon out.json -t comment # 仅注释
python degpt/role.py -f testcase/fibon out.json -t rename  # 仅重命名
```

### Web UI 模式

```bash
cd web_ui
python app.py
# 访问 http://localhost:5000
```

## 📂 输出位置

- JSON 结果：`output/<输出名称>.json`
- 优化代码：`output/<输出名称>_opt.c`

## ✅ 验证安装

```bash
# 测试依赖
python -c "import openai, tiktoken, Levenshtein, cinspector; print('OK')"

# 测试 API
python degpt/test_api.py
```

## 🔧 常见问题

| 问题 | 解决方案 |
|------|---------|
| 找不到 Python | 使用 `py` 或 `python3` |
| 模块未找到 | `pip install -r requirements.txt` |
| cinspector 安装失败 | 安装编译工具（见用户手册） |
| API 连接失败 | 检查 `config.ini` 中的 `api_key` |
| 端口被占用 | 修改 `web_ui/app.py` 中的端口号 |

## 📚 详细文档

- **完整手册**: [USER_MANUAL.md](USER_MANUAL.md)
- **安装指南**: [INSTALL_GUIDE.md](INSTALL_GUIDE.md)
- **运行指南**: [运行指南_阿里云Qwen.md](运行指南_阿里云Qwen.md)

---

**提示**: 遇到问题请查看 `USER_MANUAL.md` 的"常见问题"和"故障排除"章节。


