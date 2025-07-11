#!/usr/bin/env python3
"""
独立测试版本 - 不依赖外部包，仅测试解析逻辑
"""
import os
import json

def load_env_config():
    """加载环境配置"""
    config = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    return config

def parse_user_input_standalone(user_input: str) -> dict:
    """
    独立解析用户输入（不调用API）
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
    
    # 提取搜索关键词
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
    
    # 确保搜索词不为空
    if not search_query:
        search_query = "默认搜索"
    
    return {
        "intent": "open_and_search",
        "website_name": website_name,
        "website_url": website_url,
        "search_query": search_query
    }

def print_task_info(task_info):
    """打印任务信息"""
    print("\n📋 任务解析结果:")
    print(f"   意图: {task_info.get('intent', 'unknown')}")
    print(f"   网站: {task_info.get('website_name', 'unknown')}")
    print(f"   链接: {task_info.get('website_url', 'unknown')}")
    print(f"   搜索: {task_info.get('search_query', 'unknown')}")
    print("-" * 60)
    
    # 验证必要字段
    required_fields = ['intent', 'website_url', 'search_query']
    missing_fields = []
    
    for field in required_fields:
        if field not in task_info or not task_info[field]:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"⚠️  警告: 缺少字段 {missing_fields}")
        return False
    
    return True

def simulate_browser_task(task_info):
    """模拟浏览器任务"""
    print(f"🌐 模拟打开: {task_info['website_url']}")
    print(f"🔍 模拟搜索: {task_info['search_query']}")
    print("✅ 模拟任务完成")

def main():
    """主函数"""
    print("🤖 智能浏览器控制系统 - 独立测试版")
    print("=" * 60)
    print("功能：测试自然语言解析功能")
    print("注意：这是测试版，不会真正打开浏览器")
    print("=" * 60)
    
    # 加载配置
    config = load_env_config()
    if 'QWEN_API_KEY' in config:
        print(f"✅ 检测到API配置: {config['QWEN_API_KEY'][:10]}...")
    else:
        print("⚠️  未检测到API配置，使用本地解析")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n请输入指令 (或输入 'quit' 退出): ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 测试结束，再见！")
                break
            
            # 检查空输入
            if not user_input:
                print("⚠️  请输入有效的指令")
                continue
            
            print(f"\n🔍 正在解析指令: {user_input}")
            
            # 解析用户输入
            task_info = parse_user_input_standalone(user_input)
            
            # 显示解析结果并验证
            is_valid = print_task_info(task_info)
            
            if not is_valid:
                print("❌ 任务信息不完整")
                continue
            
            # 确认执行
            confirm = input("是否模拟执行此任务？(y/n): ").strip().lower()
            if confirm not in ['y', 'yes', '是']:
                print("❌ 任务已取消")
                continue
            
            # 模拟执行任务
            print("\n🚀 开始模拟任务...")
            if task_info.get("intent") == "open_and_search":
                simulate_browser_task(task_info)
            else:
                print("⚠️  暂不支持此类型的任务")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！")
            break
        except Exception as e:
            print(f"❌ 执行时发生错误: {e}")

if __name__ == "__main__":
    main()