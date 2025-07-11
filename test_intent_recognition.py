#!/usr/bin/env python3
"""
测试意图识别修复效果
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qwen_agent import parse_user_input

def test_intent_recognition():
    """测试各种用户输入的意图识别"""
    print("🧪 测试意图识别修复效果")
    print("=" * 60)
    
    # 测试案例
    test_cases = [
        # 原问题案例
        {
            "input": "查看今天广州天气",
            "expected_intent": "open_and_search",
            "description": "天气查询（原问题）"
        },
        
        # 信息查看类
        {
            "input": "查看最新新闻",
            "expected_intent": "open_and_search", 
            "description": "新闻查看"
        },
        {
            "input": "了解人工智能发展",
            "expected_intent": "open_and_search",
            "description": "了解信息"
        },
        {
            "input": "看看今天股价",
            "expected_intent": "open_and_search",
            "description": "股价查看"
        },
        
        # 学习需求类
        {
            "input": "学习Python编程",
            "expected_intent": "open_and_search",
            "description": "学习需求"
        },
        {
            "input": "怎么做蛋糕",
            "expected_intent": "open_and_search",
            "description": "教程查询"
        },
        
        # 明确搜索类
        {
            "input": "搜索机器学习资料", 
            "expected_intent": "open_and_search",
            "description": "明确搜索"
        },
        {
            "input": "在知乎找AI讨论",
            "expected_intent": "open_and_search",
            "description": "指定网站搜索"
        },
        
        # 单纯打开网站类
        {
            "input": "打开百度",
            "expected_intent": "open_website",
            "description": "单纯打开网站"
        },
        {
            "input": "访问知乎",
            "expected_intent": "open_website", 
            "description": "访问网站"
        },
        {
            "input": "去微博",
            "expected_intent": "open_website",
            "description": "去网站"
        },
        
        # 登录类
        {
            "input": "登录知乎 用户名test 密码123",
            "expected_intent": "open_and_login",
            "description": "登录请求"
        }
    ]
    
    correct_count = 0
    total_count = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 [测试{i}] {case['description']}")
        print(f"📝 [输入] {case['input']}")
        print(f"🎯 [期望] intent: {case['expected_intent']}")
        
        try:
            result = parse_user_input(case['input'])
            actual_intent = result.get('intent', 'unknown')
            
            print(f"📊 [实际] intent: {actual_intent}")
            print(f"🔍 [搜索] search_query: '{result.get('search_query', '')}'")
            print(f"🌐 [网站] {result.get('website_name', '')} -> {result.get('website_url', '')}")
            
            if actual_intent == case['expected_intent']:
                print("✅ [结果] 意图识别正确")
                correct_count += 1
            else:
                print("❌ [结果] 意图识别错误")
            
        except Exception as e:
            print(f"❌ [错误] 解析失败: {e}")
        
        print("-" * 40)
    
    # 统计结果
    print(f"\n📊 测试统计:")
    print(f"总测试数: {total_count}")
    print(f"正确识别: {correct_count}")
    print(f"准确率: {correct_count/total_count*100:.1f}%")
    
    if correct_count == total_count:
        print("🎉 所有测试通过！意图识别修复成功！")
    elif correct_count >= total_count * 0.8:
        print("✅ 大部分测试通过，意图识别显著改善")
    else:
        print("⚠️  仍有较多问题，需要进一步优化")

def test_specific_case():
    """专门测试原问题案例"""
    print("\n" + "=" * 60)
    print("🎯 专项测试：天气查询问题")
    print("=" * 60)
    
    test_input = "查看今天广州天气"
    print(f"📝 测试输入: {test_input}")
    
    result = parse_user_input(test_input)
    
    print(f"\n📊 解析结果:")
    print(f"   意图: {result.get('intent')}")
    print(f"   网站: {result.get('website_name')}")
    print(f"   链接: {result.get('website_url')}")
    print(f"   搜索: {result.get('search_query')}")
    
    if result.get('intent') == 'open_and_search':
        print("\n✅ 修复成功！现在能正确识别为搜索任务")
    else:
        print(f"\n❌ 修复失败！仍然识别为: {result.get('intent')}")

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 完整测试 (测试所有场景)")
    print("2. 专项测试 (只测试天气查询问题)")
    
    choice = input("请输入选择 (1 或 2, 默认为2): ").strip()
    
    if choice == "1":
        test_intent_recognition()
    else:
        test_specific_case()