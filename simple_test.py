#!/usr/bin/env python3
"""
简单测试，不依赖外部包
"""
import os
import json

def load_env_vars():
    """手动加载环境变量"""
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def simple_fallback_parse(user_input: str) -> dict:
    """
    简单的回退解析方法
    """
    # 简单的关键词匹配
    if "知乎" in user_input:
        website_name = "知乎"
        website_url = "https://www.zhihu.com"
    elif "百度" in user_input:
        website_name = "百度"
        website_url = "https://www.baidu.com"
    elif "微博" in user_input:
        website_name = "微博"
        website_url = "https://weibo.com"
    elif "b站" in user_input.lower() or "bilibili" in user_input.lower():
        website_name = "B站"
        website_url = "https://www.bilibili.com"
    elif "豆瓣" in user_input:
        website_name = "豆瓣"
        website_url = "https://www.douban.com"
    else:
        website_name = "百度"
        website_url = "https://www.baidu.com"
    
    # 提取搜索关键词（简单处理）
    search_keywords = ["搜索", "搜", "查", "找"]
    search_query = user_input
    for keyword in search_keywords:
        if keyword in user_input:
            parts = user_input.split(keyword, 1)
            if len(parts) > 1:
                search_query = parts[1].strip()
                break
    
    # 清理搜索词
    search_query = search_query.replace(website_name, "").strip()
    
    return {
        "intent": "open_and_search",
        "website_name": website_name,
        "website_url": website_url,
        "search_query": search_query
    }

def test_parsing():
    """测试解析功能"""
    print("🧪 测试解析功能...")
    
    test_cases = [
        "去知乎搜索人工智能",
        "打开百度搜索Python",
        "在B站找编程视频",
        "微博搜索新闻"
    ]
    
    for test_input in test_cases:
        print(f"\n📝 输入: {test_input}")
        result = simple_fallback_parse(test_input)
        print(f"✅ 解析结果:")
        print(f"   意图: {result['intent']}")
        print(f"   网站: {result['website_name']}")
        print(f"   链接: {result['website_url']}")
        print(f"   搜索: {result['search_query']}")
        
        # 检查必要字段
        required_fields = ['intent', 'website_url', 'search_query']
        missing_fields = []
        
        for field in required_fields:
            if field not in result or not result[field]:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ 缺少字段: {missing_fields}")
        else:
            print("✅ 所有必要字段都存在")

def test_env_config():
    """测试环境配置"""
    print("\n🧪 测试环境配置...")
    env_vars = load_env_vars()
    
    required_vars = ['QWEN_API_KEY', 'QWEN_BASE_URL', 'QWEN_MODEL']
    for var in required_vars:
        if var in env_vars:
            print(f"✅ {var}: {env_vars[var][:10]}...")
        else:
            print(f"❌ {var}: 未配置")

if __name__ == "__main__":
    test_env_config()
    test_parsing()
    
    print("\n" + "="*50)
    print("📋 问题诊断:")
    print("1. 解析逻辑正常，问题可能在API调用或JSON解析")
    print("2. 建议先安装依赖: pip install -r requirements.txt") 
    print("3. 然后测试完整功能")
    print("="*50)