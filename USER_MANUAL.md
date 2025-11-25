# DeGPT 用户手册

## 目录

1. [项目简介](#项目简介)
2. [系统要求](#系统要求)
3. [从零开始安装](#从零开始安装)
4. [配置说明](#配置说明)
5. [运行方式](#运行方式)
6. [使用示例](#使用示例)
7. [常见问题](#常见问题)
8. [故障排除](#故障排除)

---

## 项目简介

DeGPT 是一个使用大语言模型（LLM）优化反编译器输出的工具，发表于 NDSS 2024。该项目采用三角色协作模型：

- **Referee（裁判）**：评估反编译代码并提供优化方向建议
- **Advisor（顾问）**：根据裁判的建议，提供具体的代码修改方案
- **Operator（操作员）**：执行修改并确保代码语义正确性

### 主要功能

- 🔧 代码简化：简化复杂的反编译代码结构
- 💬 添加注释：为代码添加有意义的注释
- 🏷️ 变量重命名：将无意义的变量名重命名为有意义的名称
- 🌐 Web界面：提供友好的可视化交互界面
- 📊 批量处理：支持命令行批量处理多个文件

---

## 系统要求

### 必需环境

- **操作系统**：Windows 10/11, Linux, macOS
- **Python版本**：Python 3.9 或更高版本（推荐 3.9-3.11）
- **内存**：至少 4GB RAM（推荐 8GB+）
- **网络**：需要能够访问 LLM API 服务（如阿里云 DashScope、OpenAI 等）

### 推荐配置

- Python 3.10 或 3.11
- 8GB+ RAM
- 稳定的网络连接

---

## 从零开始安装

### 步骤 1：检查 Python 环境

首先确认您的系统已安装 Python：

```bash
python --version
```

或者：

```bash
python3 --version
```

**如果未安装 Python**：

- **Windows**：从 [python.org](https://www.python.org/downloads/) 下载安装，安装时勾选 "Add Python to PATH"
- **Linux**：使用包管理器安装，例如：
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip
  ```
- **macOS**：使用 Homebrew：
  ```bash
  brew install python3
  ```

### 步骤 2：获取项目代码

如果您还没有项目代码，请从仓库克隆或下载：

```bash
git clone <repository-url>
cd DeGPTplus_backup
```

### 步骤 3：安装项目依赖

#### 3.1 安装基础 Python 包

在项目根目录下，运行：

```bash
pip install -r requirements.txt
```

如果 `pip` 命令不可用，尝试：

```bash
python -m pip install -r requirements.txt
```

或者：

```bash
python3 -m pip install -r requirements.txt
```

#### 3.2 安装 cinspector（必需）

`cinspector` 是 C 代码分析框架，需要单独安装：

**方法 A：从 GitHub 安装（推荐）**

```bash
git clone https://github.com/PeiweiHu/cinspector
cd cinspector
pip install .
cd ..
```

**方法 B：如果项目已包含 cinspector 目录**

```bash
cd cinspector
pip install .
cd ..
```

**注意**：安装 cinspector 可能需要编译 C 扩展，确保您的系统已安装：
- **Windows**：Visual Studio Build Tools 或 MinGW
- **Linux**：`build-essential` 包（`sudo apt install build-essential`）
- **macOS**：Xcode Command Line Tools（`xcode-select --install`）

#### 3.3 安装 Web UI 依赖（可选）

如果您要使用 Web 界面，需要额外安装：

```bash
cd web_ui
pip install -r requirements.txt
cd ..
```

### 步骤 4：验证安装

运行以下命令验证关键依赖是否安装成功：

```bash
python -c "import openai; print('openai: OK')"
python -c "import tiktoken; print('tiktoken: OK')"
python -c "import Levenshtein; print('python-levenshtein: OK')"
python -c "import cinspector; print('cinspector: OK')"
```

如果所有模块都能正常导入，说明安装成功。

---

## 配置说明

### 配置文件位置

配置文件位于：`degpt/config.ini`

### 创建配置文件

如果 `degpt/config.ini` 不存在，请复制示例配置：

```bash
cp degpt/config_example.ini degpt/config.ini
```

### 配置 LLM API

编辑 `degpt/config.ini` 文件：

```ini
[LLM]
model = qwen-turbo
api_key = YOUR_API_KEY_HERE
api_base = https://dashscope.aliyuncs.com/compatible-mode/v1
temperature = 0.2
```

#### 配置项说明

- **model**：要使用的模型名称
  - 阿里云 Qwen：`qwen-turbo`, `qwen-plus`, `qwen-max`
  - OpenAI：`gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`
  - DeepSeek：`deepseek-chat`
  - 其他兼容 OpenAI API 的模型

- **api_key**：您的 API 密钥
  - **重要**：请妥善保管，不要泄露给他人

- **api_base**：API 服务的基础 URL
  - 阿里云 DashScope：`https://dashscope.aliyuncs.com/compatible-mode/v1`
  - OpenAI：`https://api.openai.com/v1`
  - DeepSeek：`https://api.deepseek.com/v1`
  - 本地模型：`http://localhost:端口/v1`

- **temperature**：生成温度（0.0-2.0），控制输出的随机性
  - 推荐值：0.2（更稳定）或 0.7（更有创造性）

### 获取 API 密钥

#### 阿里云 DashScope（推荐）

1. 访问 [阿里云 DashScope 控制台](https://dashscope.aliyun.com/)
2. 登录您的阿里云账号（如无账号需先注册并完成实名认证）
3. 开通"通义千问"服务
4. 在"API Key管理"页面创建新的 API Key
5. 复制生成的 API Key（格式类似：`sk-xxxxxxxxxxxxx`）

#### OpenAI

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 登录并创建 API Key
3. 复制 API Key

#### DeepSeek

1. 访问 [DeepSeek 控制台](https://platform.deepseek.com/)
2. 登录并创建 API Key
3. 复制 API Key

### 验证配置

运行测试脚本验证配置是否正确：

```bash
python degpt/test_api.py
```

如果看到成功消息，说明配置正确。

---

## 运行方式

### 方式一：命令行运行（推荐用于批量处理）

#### 基本命令格式

```bash
python degpt/role.py -f <输入文件> <输出名称>
```

#### 参数说明

- `-f` 或 `--file`：从文件读取输入
- `-s` 或 `--string`：从字符串输入
- `-t`：指定优化类型（可选）
  - `all`：全部优化（默认）
  - `simplify`：仅简化代码
  - `comment`：仅添加注释
  - `rename`：仅重命名变量

#### 使用示例

**示例 1：优化文件**

```bash
python degpt/role.py -f testcase/fibon out.json
```

**示例 2：指定优化类型**

```bash
# 只进行变量重命名
python degpt/role.py -f testcase/fibon out.json -t rename

# 只进行代码简化
python degpt/role.py -f testcase/fibon out.json -t simplify

# 只添加注释
python degpt/role.py -f testcase/fibon out.json -t comment

# 执行所有优化（默认）
python degpt/role.py -f testcase/fibon out.json -t all
```

**示例 3：使用字符串输入**

```bash
python degpt/role.py -s "int main() { return 0; }" test_output
```

#### 输出结果

运行完成后，结果文件将保存在 `output/` 目录下：

- `<输出名称>.json`：包含完整的优化过程记录（JSON 格式）
- `<输出名称>_opt.c`：优化后的 C 代码文件

### 方式二：Web UI 运行（推荐用于交互式使用）

#### 启动 Web 服务

**Windows 用户（推荐）**：

```bash
cd web_ui
# 双击运行 start.bat 或 run_simple.bat
# 或手动运行：
python app.py
```

**Linux/macOS 用户**：

```bash
cd web_ui
python app.py
```

或使用 Python 3：

```bash
cd web_ui
python3 app.py
```

#### 访问界面

启动成功后，在浏览器中访问：

```
http://localhost:5000
```

#### 使用 Web 界面

1. **检查配置**：页面加载时会自动检查 LLM 配置状态
2. **输入代码**：在代码输入框中粘贴或输入反编译的 C 代码
3. **选择优化类型**：
   - 全部优化：执行所有优化步骤
   - 简化代码：仅简化代码结构
   - 添加注释：仅添加代码注释
   - 重命名变量：仅重命名变量
4. **开始优化**：点击"开始优化"按钮，等待处理完成
5. **查看结果**：在结果区域查看原始代码和优化后的代码对比

#### 停止服务

在运行服务的终端窗口中按 `Ctrl+C` 停止服务。

---

## 使用示例

### 示例 1：优化单个文件

假设您有一个反编译的 C 代码文件 `decompiled.c`：

```c
int func_001(int a1, int a2) {
    int v1 = a1 + a2;
    int v2 = v1 * 2;
    return v2;
}
```

运行优化：

```bash
python degpt/role.py -f decompiled.c result
```

优化后的代码可能变成：

```c
// 计算两个数的和，然后乘以2
int calculate_double_sum(int num1, int num2) {
    int sum = num1 + num2;
    int doubled = sum * 2;
    return doubled;
}
```

### 示例 2：批量处理

创建一个批处理脚本 `batch_process.sh`（Linux/macOS）：

```bash
#!/bin/bash
for file in testcase/*.c; do
    filename=$(basename "$file" .c)
    echo "Processing $file..."
    python degpt/role.py -f "$file" "$filename"
done
```

Windows 批处理脚本 `batch_process.bat`：

```batch
@echo off
for %%f in (testcase\*.c) do (
    echo Processing %%f...
    python degpt/role.py -f "%%f" "%%~nf"
)
```

### 示例 3：使用 Web UI

1. 启动 Web 服务
2. 在浏览器中打开 `http://localhost:5000`
3. 将反编译代码粘贴到输入框
4. 选择优化类型
5. 点击"开始优化"
6. 查看优化结果并复制

---

## 常见问题

### Q1：找不到 Python 命令

**问题**：运行 `python` 命令时提示"不是内部或外部命令"

**解决方案**：

1. 确认 Python 已安装：`py --version` 或 `python3 --version`
2. 将 Python 添加到系统 PATH
3. 使用完整路径运行：`C:\Python39\python.exe degpt/role.py`

### Q2：模块未找到（ModuleNotFoundError）

**问题**：运行时提示 `ModuleNotFoundError: No module named 'xxx'`

**解决方案**：

```bash
# 重新安装依赖
pip install -r requirements.txt

# 如果使用虚拟环境，确保已激活
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Q3：cinspector 安装失败

**问题**：安装 cinspector 时出现编译错误

**解决方案**：

1. **Windows**：安装 Visual Studio Build Tools
   - 下载：https://visualstudio.microsoft.com/downloads/
   - 选择 "C++ build tools"

2. **Linux**：安装编译工具
   ```bash
   sudo apt install build-essential python3-dev
   ```

3. **macOS**：安装 Xcode Command Line Tools
   ```bash
   xcode-select --install
   ```

### Q4：API 连接失败

**问题**：运行时提示 API 连接错误

**解决方案**：

1. 检查 `config.ini` 中的 `api_key` 是否正确
2. 检查网络连接是否正常
3. 确认 API 密钥是否有效且有足够余额
4. 检查防火墙/代理设置
5. 运行测试脚本：`python degpt/test_api.py`

### Q5：端口被占用（Web UI）

**问题**：启动 Web UI 时提示端口 5000 已被占用

**解决方案**：

修改 `web_ui/app.py` 最后一行：

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为其他端口
```

### Q6：编码错误（Windows）

**问题**：运行批处理文件时出现编码错误

**解决方案**：

1. 使用 `start.bat` 或 `run_simple.bat`（已修复编码问题）
2. 直接在命令行运行：`python web_ui/app.py`
3. 使用 PowerShell 而不是 CMD

---

## 故障排除

### 检查清单

在报告问题前，请确认：

- [ ] Python 版本 >= 3.9
- [ ] 所有依赖已正确安装
- [ ] cinspector 已安装
- [ ] `config.ini` 已正确配置
- [ ] API 密钥有效且有余额
- [ ] 网络连接正常

### 查看日志

程序运行时会生成日志文件：

- `degpt/log.log`：详细的运行日志
- `chat_log.json`：LLM 交互记录

查看日志可以帮助诊断问题：

```bash
# 查看最新日志
tail -f degpt/log.log

# Windows PowerShell
Get-Content degpt/log.log -Tail 50 -Wait
```

### 测试各个组件

**测试 Python 环境**：

```bash
python --version
python -c "import sys; print(sys.version)"
```

**测试依赖安装**：

```bash
python -c "import openai, tiktoken, Levenshtein, cinspector; print('All OK')"
```

**测试 API 连接**：

```bash
python degpt/test_api.py
```

**测试 cinspector**：

```python
from cinspector.interfaces import CCode
code = CCode("int main() { return 0; }")
print("cinspector OK")
```

### 获取帮助

如果问题仍未解决：

1. 查看项目 README 文件
2. 检查 GitHub Issues
3. 查看日志文件获取详细错误信息
4. 确认您使用的是最新版本的代码

---

## 附录

### A. 项目结构

```
DeGPTplus_backup/
├── degpt/              # 核心代码目录
│   ├── chat.py        # LLM 交互接口
│   ├── role.py        # 三角色模型实现
│   ├── util.py        # 工具函数
│   ├── mssc.py        # 语义比较
│   ├── config.ini     # 配置文件（需配置）
│   └── ...
├── web_ui/            # Web 界面
│   ├── app.py         # Flask 应用
│   ├── templates/     # HTML 模板
│   ├── static/        # 静态资源
│   └── requirements.txt
├── cinspector/        # C 代码分析框架
├── output/            # 输出目录
├── testcase/          # 测试用例
├── requirements.txt   # 项目依赖
└── USER_MANUAL.md     # 本手册
```

### B. 输出文件格式

输出的 JSON 文件包含以下信息：

```json
{
  "decompiler_output": "原始反编译代码",
  "source_code": "源代码（如果提供）",
  "workflow": "工作流状态",
  "original_directions": "裁判建议的优化方向",
  "sorted_directions": "排序后的优化方向",
  "optimization": [
    {
      "input": "输入代码",
      "output": "输出代码",
      "status": "状态",
      "advisor": "顾问的建议",
      "operator": "操作员的执行结果"
    }
  ],
  "output": "最终优化后的代码"
}
```

### C. 支持的模型

- **阿里云 Qwen**：qwen-turbo, qwen-plus, qwen-max
- **OpenAI**：gpt-3.5-turbo, gpt-4, gpt-4-turbo
- **DeepSeek**：deepseek-chat
- **其他**：任何兼容 OpenAI API 格式的模型

### D. 性能优化建议

1. **使用更快的模型**：对于批量处理，使用 `qwen-turbo` 或 `gpt-3.5-turbo`
2. **调整 temperature**：降低 temperature 可以提高稳定性
3. **批量处理**：使用命令行模式进行批量处理，避免 Web UI 的开销
4. **网络优化**：确保网络连接稳定，减少超时错误

---

**最后更新**：2024年

**版本**：1.0

---

