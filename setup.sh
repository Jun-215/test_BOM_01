#!/bin/bash
# 智能浏览器控制系统 - 环境设置脚本

echo "🚀 开始设置智能浏览器控制系统..."
echo "=================================="

# 检查Python版本
echo "📋 检查Python版本..."
python3 --version

# 创建虚拟环境
echo "🐍 创建虚拟环境..."
python3 -m venv browser_env

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source browser_env/bin/activate

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 测试安装
echo "🧪 测试系统..."
python3 simple_test.py

echo "=================================="
echo "🎉 设置完成！"
echo "📋 使用方法："
echo "   1. 激活虚拟环境: source browser_env/bin/activate"
echo "   2. 运行程序: python3 main.py"
echo "   3. 或者直接测试: python3 main.py '去知乎搜索人工智能'"
echo "=================================="