#!/usr/bin/env python3
"""
简单的系统测试脚本
"""
import os
import sys

def test_environment():
    """测试环境配置"""
    print("🧪 测试环境配置...")
    
    # 检查.env文件
    if os.path.exists('.env'):
        print("✅ .env文件存在")
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'QWEN_API_KEY' in content:
                print("✅ QWEN_API_KEY已配置")
            else:
                print("❌ QWEN_API_KEY未配置")
    else:
        print("❌ .env文件不存在")
    
    # 检查Python版本
    print(f"✅ Python版本: {sys.version}")
    
    print()

def test_modules():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    
    # 测试标准库
    try:
        import json
        import asyncio
        print("✅ 标准库导入成功")
    except ImportError as e:
        print(f"❌ 标准库导入失败: {e}")
    
    # 测试第三方库
    required_modules = ['requests', 'dotenv', 'pyppeteer']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} 导入成功")
        except ImportError:
            print(f"❌ {module} 导入失败，请运行: pip install {module}")
    
    print()

def test_file_structure():
    """测试文件结构"""
    print("🧪 测试文件结构...")
    
    required_files = [
        'main.py',
        'qwen_agent.py', 
        'browser_controller.py',
        'utils.py',
        '.env',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
    
    # 检查prompts目录
    if os.path.exists('prompts') and os.path.exists('prompts/intent_prompt.txt'):
        print("✅ prompts目录和模板文件存在")
    else:
        print("❌ prompts目录或模板文件不存在")
    
    print()

def test_config_parsing():
    """测试配置解析"""
    print("🧪 测试配置解析...")
    
    try:
        # 简单的配置解析测试
        config = {}
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
            
            print(f"✅ 配置解析成功，找到{len(config)}个配置项")
            
            # 检查必要配置
            required_configs = ['QWEN_API_KEY', 'QWEN_BASE_URL', 'QWEN_MODEL']
            for cfg in required_configs:
                if cfg in config:
                    print(f"✅ {cfg} 已配置")
                else:
                    print(f"❌ {cfg} 未配置")
        else:
            print("❌ .env文件不存在")
            
    except Exception as e:
        print(f"❌ 配置解析失败: {e}")
    
    print()

def test_intent_parsing():
    """测试意图解析（不调用API）"""
    print("🧪 测试意图解析逻辑...")
    
    try:
        # 简单的意图解析测试
        test_cases = [
            "去知乎搜索人工智能",
            "打开百度搜索Python",
            "在B站找编程视频",y
            "微博搜索新闻"
        ]
        
        for test_input in test_cases:
            # 简单的解析逻辑
            if "知乎" in test_input:
                website = "知乎"
                url = "https://www.zhihu.com"
            elif "百度" in test_input:
                website = "百度"
                url = "https://www.baidu.com"
            elif "B站" in test_input.lower() or "b站" in test_input:
                website = "B站"
                url = "https://www.bilibili.com"
            elif "微博" in test_input:
                website = "微博"
                url = "https://weibo.com"
            else:
                website = "百度"
                url = "https://www.baidu.com"
            
            # 提取搜索词
            search_keywords = ["搜索", "搜", "找"]
            search_query = test_input
            for keyword in search_keywords:
                if keyword in test_input:
                    parts = test_input.split(keyword, 1)
                    if len(parts) > 1:
                        search_query = parts[1].strip()
                        break
            
            search_query = search_query.replace(website, "").strip()
            
            print(f"✅ 输入: {test_input}")
            print(f"   网站: {website} ({url})")
            print(f"   搜索: {search_query}")
            print()
            
    except Exception as e:
        print(f"❌ 意图解析测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始系统测试...")
    print("=" * 60)
    
    test_environment()
    test_modules()
    test_file_structure()
    test_config_parsing()
    test_intent_parsing()
    
    print("=" * 60)
    print("🏁 测试完成！")
    print()
    print("📋 下一步操作：")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 运行程序: python3 main.py")
    print("3. 测试指令: '去知乎搜索人工智能'")

if __name__ == "__main__":
    main()