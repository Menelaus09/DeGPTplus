# DeGPT Web UI 启动指南

## 问题解决

如果遇到编码错误（如 'thon' 不是内部或外部命令），这是因为批处理文件的编码问题。

## 启动方法

### 方法1：使用简化脚本（推荐）

直接双击 `start.bat` 或 `run_simple.bat`

这两个脚本最简单，避免了编码问题。

### 方法2：使用完整脚本

双击 `run.bat`（已修复编码问题，使用英文提示）

### 方法3：手动启动（最可靠）

1. 打开命令提示符（CMD）或 PowerShell
2. 进入 `DeGPT/web_ui` 目录：
   ```bash
   cd D:\load\mycode1\DeGPT\web_ui
   ```
3. 运行：
   ```bash
   python app.py
   ```
   或
   ```bash
   py app.py
   ```

### 方法4：使用 PowerShell

在 PowerShell 中：
```powershell
cd D:\load\mycode1\DeGPT\web_ui
python app.py
```

## 常见问题

### 问题1：找不到 Python

**解决方案**：
- 确保 Python 已安装
- 将 Python 添加到系统 PATH
- 或使用 `py` 命令（Python Launcher）

### 问题2：找不到 flask 模块

**解决方案**：
```bash
pip install -r requirements.txt
```

### 问题3：编码错误

**解决方案**：
- 使用 `start.bat` 或 `run_simple.bat`
- 或直接在命令行运行 `python app.py`

### 问题4：端口被占用

**解决方案**：
- 修改 `app.py` 最后一行，改为其他端口：
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

## 验证安装

运行以下命令检查：
```bash
python --version
python -c "import flask; print('Flask OK')"
```

## 访问界面

启动成功后，在浏览器中访问：
- http://localhost:5000

## 停止服务器

在运行脚本的窗口中按 `Ctrl+C`



