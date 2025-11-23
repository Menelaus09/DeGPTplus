#!/bin/bash

echo "========================================"
echo "DeGPT Web UI 启动脚本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python"
    exit 1
fi

echo "[信息] 正在检查依赖..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "[警告] Flask未安装，正在安装依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo "[信息] 启动Web服务器..."
echo "[信息] 请在浏览器中访问: http://localhost:5000"
echo "[信息] 按 Ctrl+C 停止服务器"
echo ""

python3 app.py





