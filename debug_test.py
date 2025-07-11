#!/usr/bin/env python3
"""
调试千问API解析问题
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qwen_agent import parse_user_input

def test_qwen_parsing():
    """测试千问API解析"""
    test_cases = [
        "去知乎搜索人工智能",
        "打开百度搜索Python",
        "在B站找编程视频"
    ]
    
    for test_input in test_cases:
        print(f"\n🧪 测试输入: {test_input}")
        try:
            result = parse_user_input(test_input)
            print(f"✅ 解析结果: {result}")
            print(f"   类型: {type(result)}")
            
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
                
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_qwen_parsing()