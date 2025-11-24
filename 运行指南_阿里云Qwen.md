# DeGPT 使用阿里云Qwen-Turbo运行指南

## 项目背景

DeGPT是一个使用大语言模型（LLM）优化反编译器输出的工具，发表于NDSS 2024。该项目采用三角色协作模型：

- **Referee（裁判）**：评估反编译代码并提供优化方向建议
- **Advisor（顾问）**：根据裁判的建议，提供具体的代码修改方案
- **Operator（操作员）**：执行修改并确保代码语义正确性

本指南将帮助您配置并使用阿里云通义千问（Qwen-Turbo）模型来运行DeGPT。

## 一、环境准备

### 1.1 检查Python环境

确保已安装Python 3.9或更高版本：

```bash
python --version
```

### 1.2 激活虚拟环境（如果使用）

如果项目使用虚拟环境，请先激活：

**Windows:**
```bash
degpt_env\Scripts\activate
```

**Linux/Mac:**
```bash
source degpt_env/bin/activate
```

### 1.3 安装依赖

确保已安装以下依赖包：

```bash
pip install openai==1.28.1 tiktoken==0.2.0 python-levenshtein
```

**注意**：`cinspector` 需要单独安装，如果尚未安装，请参考项目README。

## 二、配置阿里云API密钥

### 2.1 获取阿里云API密钥

1. 访问阿里云DashScope控制台：https://dashscope.aliyun.com/
2. 登录您的阿里云账号（如无账号需先注册并完成实名认证）
3. 开通"通义千问"服务
4. 在"API Key管理"页面创建新的API Key
5. 复制生成的API Key（格式类似：`sk-xxxxxxxxxxxxx`）

### 2.2 配置API密钥

**重要**：API密钥配置位置在 `DeGPT/degpt/config.ini` 文件中。

打开 `DeGPT/degpt/config.ini` 文件，您会看到以下内容：

```ini
[LLM]
model = qwen-turbo
api_key =
api_base = https://dashscope.aliyuncs.com/compatible-mode/v1
```

**在 `api_key =` 后面填入您的阿里云API密钥**，例如：

```ini
[LLM]
model = qwen-turbo
api_key = sk-xxxxxxxxxxxxx  # 在这里填入您的API密钥
api_base = https://dashscope.aliyuncs.com/compatible-mode/v1
```

**配置说明**：
- `model`: 已设置为 `qwen-turbo`，这是阿里云通义千问的快速模型
- `api_key`: **您需要在这里填入从阿里云DashScope获取的API密钥**
- `api_base`: 已配置为阿里云兼容模式地址，无需修改

## 三、运行DeGPT

### 3.1 基本运行命令

进入项目根目录（`DeGPT`），运行以下命令：

```bash
python degpt/role.py -f testcase/fibon out.json
```

**参数说明**：
- `-f`: 指定输入文件模式
- `testcase/fibon`: 输入文件路径（反编译的C代码文件）
- `out.json`: 输出文件名（将保存在 `output/` 目录下）

### 3.2 其他运行选项

**使用字符串输入：**
```bash
python degpt/role.py -s "您的C代码字符串" output_name
```

**指定优化类型：**
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

### 3.3 查看运行结果

运行完成后，结果文件将保存在 `DeGPT/output/` 目录下：

- `out.json`: 包含完整的优化过程记录（JSON格式）
- `out_opt.c`: 优化后的C代码文件

查看结果：
```bash
# 查看JSON结果
cat output/out.json

# 查看优化后的代码
cat output/out_opt.c
```

## 四、验证配置

### 4.1 测试API连接

如果遇到问题，可以使用以下Python代码测试API连接：

```python
from openai import OpenAI

client = OpenAI(
    api_key="您的API密钥",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

response = client.chat.completions.create(
    model="qwen-turbo",
    messages=[
        {"role": "user", "content": "你好，请说出你的名字"}
    ]
)

print(response.choices[0].message.content)
```

如果成功输出模型回复，说明API配置正确。

### 4.2 检查配置文件

运行前，程序会自动检查配置。如果配置不完整，会提示：

```
please complete llm access setup first...
```

此时请检查 `config.ini` 文件中的 `api_key` 是否已正确填写。

## 五、运行过程记录

### 5.1 日志文件

程序运行过程中会生成日志文件：
- `DeGPT/degpt/log.log`: 详细的运行日志

### 5.2 聊天记录

LLM的交互记录会保存在：
- `chat_log.json`: 包含所有与LLM的对话历史

### 5.3 输出JSON结构

输出的JSON文件包含以下信息：
- `decompiler_output`: 原始反编译代码
- `source_code`: 源代码（如果提供）
- `workflow`: 工作流状态（INIT/REFEREE/OPT:SIMPLIFY/DONE）
- `original_directions`: 裁判建议的优化方向
- `sorted_directions`: 排序后的优化方向
- `optimization`: 各优化步骤的详细信息
  - `input`: 输入代码
  - `output`: 输出代码
  - `status`: 状态（SUCC/FAIL|ADVISOR/FAIL|OPERATOR）
  - `advisor`: 顾问的建议
  - `operator`: 操作员的执行结果
- `output`: 最终优化后的代码

## 六、常见问题排查

### 问题1: API密钥错误

**错误信息**: HTTP 401 或认证失败

**解决方法**:
1. 检查 `config.ini` 中的 `api_key` 是否正确填写
2. 确认API密钥在阿里云DashScope控制台中有效
3. 检查API密钥是否有足够的余额或配额

### 问题2: 连接超时

**错误信息**: 连接超时或网络错误

**解决方法**:
1. 检查网络连接是否正常
2. 确认可以访问 `dashscope.aliyuncs.com`
3. 如果使用代理，确保代理配置正确

### 问题3: 模块未找到

**错误信息**: `ModuleNotFoundError`

**解决方法**:
```bash
pip install openai==1.28.1 tiktoken==0.2.0 python-levenshtein
```

### 问题4: cinspector未安装

**错误信息**: `No module named 'cinspector'`

**解决方法**:
```bash
git clone https://github.com/PeiweiHu/cinspector
cd cinspector
pip install .
```

### 问题5: 配置文件读取错误

**错误信息**: 配置文件相关错误

**解决方法**:
1. 确认 `DeGPT/degpt/config.ini` 文件存在
2. 检查文件格式是否正确（INI格式）
3. 确认 `[LLM]` 节存在且配置项完整

## 七、总结

### 关键配置位置

**API密钥输入位置**: `DeGPT/degpt/config.ini` 文件中的 `api_key` 字段

### 快速开始步骤

1. ✅ 安装依赖：`pip install openai==1.28.1 tiktoken==0.2.0 python-levenshtein`
2. ✅ 获取阿里云API密钥：访问 https://dashscope.aliyun.com/
3. ✅ 配置API密钥：编辑 `DeGPT/degpt/config.ini`，填入 `api_key`
4. ✅ 运行程序：`python degpt/role.py -f testcase/fibon out.json`
5. ✅ 查看结果：检查 `output/out.json` 和 `output/out_opt.c`

### 运行命令速查

```bash
# 基本运行
python degpt/role.py -f testcase/fibon out.json

# 指定优化类型
python degpt/role.py -f testcase/fibon out.json -t all

# 使用字符串输入
python degpt/role.py -s "代码字符串" output_name
```

---

**注意**: 请妥善保管您的API密钥，不要将其提交到版本控制系统或公开分享。

