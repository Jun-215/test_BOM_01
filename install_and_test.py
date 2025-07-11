#!/usr/bin/env python3
"""
安装依赖并测试系统
"""
import subprocess
import sys
import os

def install_requirements():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def test_imports():
    """测试导入"""
    print("🧪 测试模块导入...")
    try:
        import requests
        import dotenv
        # import pyppeteer  # 这个包比较大，先不测试
        print("✅ 主要模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_qwen_agent():
    """测试千问代理"""
    print("🧪 测试千问代理...")
    try:
        from qwen_agent import parse_user_input
        result = parse_user_input("去知乎搜索测试")
        print(f"✅ 千问代理测试成功: {result}")
        
        # 验证必要字段
        required_fields = ['intent', 'website_url', 'search_query']
        missing_fields = []
        
        for field in required_fields:
            if field not in result or not result[field]:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️  缺少字段: {missing_fields}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 千问代理测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始安装和测试...")
    print("=" * 60)
    
    # 检查环境
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 安装依赖
    if not install_requirements():
        print("❌ 安装失败，请手动运行: pip install -r requirements.txt")
        return
    
    # 测试导入
    if not test_imports():
        print("❌ 模块导入失败")
        return
    
    # 测试千问代理
    if not test_qwen_agent():
        print("❌ 千问代理测试失败")
        return
    
    print("\n" + "=" * 60)
    print("🎉 系统测试通过！")
    print("📋 可以开始使用了:")
    print("   python3 main.py")
    print("   或者直接输入: python3 main.py '去知乎搜索人工智能'")
    print("=" * 60)

if __name__ == "__main__":
    main()