# DeGPT 快速安装指南

## 5 分钟快速开始

### 前提条件

- Python 3.9 或更高版本
- 网络连接（用于下载依赖和访问 LLM API）

### 安装步骤

#### 1. 检查 Python 环境

```bash
python --version
```

如果未安装 Python，请先安装：
- **Windows**: 从 [python.org](https://www.python.org/downloads/) 下载
- **Linux**: `sudo apt install python3 python3-pip`
- **macOS**: `brew install python3`

#### 2. 安装项目依赖

在项目根目录运行：

```bash
pip install -r requirements.txt
```

如果遇到权限问题，使用：

```bash
pip install --user -r requirements.txt
```

#### 3. 安装 cinspector（必需）

```bash
git clone https://github.com/PeiweiHu/cinspector
cd cinspector
pip install .
cd ..
```

**注意**：如果编译失败，请安装编译工具：
- **Windows**: Visual Studio Build Tools
- **Linux**: `sudo apt install build-essential python3-dev`
- **macOS**: `xcode-select --install`

#### 4. 配置 API 密钥

编辑 `degpt/config.ini` 文件：

```ini
[LLM]
model = qwen-turbo
api_key = YOUR_API_KEY_HERE
api_base = https://dashscope.aliyuncs.com/compatible-mode/v1
temperature = 0.2
```

**获取 API 密钥**：
- 阿里云 DashScope: https://dashscope.aliyun.com/
- OpenAI: https://platform.openai.com/
- DeepSeek: https://platform.deepseek.com/

#### 5. 验证安装

```bash
python degpt/test_api.py
```

如果看到成功消息，说明安装完成！

### 运行程序

#### 命令行模式

```bash
python degpt/role.py -f testcase/fibon out.json
```

#### Web UI 模式

```bash
cd web_ui
pip install -r requirements.txt
python app.py
```

然后在浏览器中访问：http://localhost:5000

### 遇到问题？

查看 [USER_MANUAL.md](USER_MANUAL.md) 获取详细文档和故障排除指南。

---

**安装时间**：约 5-10 分钟（取决于网络速度）

