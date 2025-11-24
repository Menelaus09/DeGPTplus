# cinspector 构建说明

## 问题

如果遇到错误：
```
Could not find module 'cinspector-tree-sitter.so' (or one of its dependencies)
```

这是因为 `cinspector-tree-sitter.so` 文件需要被构建。

## 解决方案

### 方法1：使用构建脚本（推荐）

在 `DeGPT/cinspector` 目录下运行：

```bash
python build_parser.py
```

### 方法2：手动构建

1. 进入 `DeGPT/cinspector/cinspector` 目录：
```bash
cd DeGPT/cinspector/cinspector
```

2. 克隆 tree-sitter-c（如果还没有）：
```bash
git clone -b v0.20.2 https://github.com/tree-sitter/tree-sitter-c.git
```

3. 构建库：
```python
from tree_sitter import Language
Language.build_library('cinspector-tree-sitter.so', ['tree-sitter-c'])
```

### 方法3：重新安装 cinspector

```bash
cd DeGPT/cinspector
pip uninstall cinspector
pip install .
```

## 前置要求

- Python 3.6+
- Git（用于克隆 tree-sitter-c）
- tree-sitter 包：`pip install tree-sitter==0.20.4`
- C 编译器（tree-sitter 需要编译 C 代码）

### Windows 上的 C 编译器

在 Windows 上，你需要安装：
- **Visual Studio Build Tools** 或
- **MinGW-w64** 或
- **Microsoft C++ Build Tools**

下载地址：
- Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
- MinGW-w64: https://www.mingw-w64.org/downloads/

## 验证

构建完成后，检查文件是否存在：
```bash
ls DeGPT/cinspector/cinspector/cinspector-tree-sitter.so
```

或在 Windows 上：
```powershell
dir DeGPT\cinspector\cinspector\cinspector-tree-sitter.so
```

## 故障排查

### 问题1：找不到 git 命令
- 确保已安装 Git 并添加到 PATH
- 或手动下载 tree-sitter-c 仓库

### 问题2：编译错误
- 确保已安装 C 编译器
- 检查 tree-sitter 版本是否正确（0.20.4）

### 问题3：在 Windows 上生成了 .pyd 而不是 .so
- tree-sitter 在 Windows 上可能生成 `.pyd` 文件
- 构建脚本会自动处理这个问题
- 或者手动重命名文件





