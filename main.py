import asyncio
import sys
from qwen_agent import parse_user_input
from browser_controller import perform_browser_task, BrowserController

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🤖 智能浏览器控制系统")
    print("=" * 60)
    print("功能：通过自然语言控制浏览器进行搜索")
    print("支持网站：知乎、百度、微博、B站、豆瓣")
    print("示例输入：'去知乎搜索大模型'、'打开百度搜索Python教程'")
    print("输入 'exit' 或 'quit' 退出程序")
    print("=" * 60)

def print_task_info(task_info):
    """打印任务信息"""
    print("\n📋 任务解析结果:")
    print(f"   意图: {task_info.get('intent', 'unknown')}")
    print(f"   网站: {task_info.get('website_name', 'unknown')}")
    print(f"   链接: {task_info.get('website_url', 'unknown')}")
    
    # 根据不同任务类型显示不同信息
    intent = task_info.get('intent', '')
    if intent == "open_and_search":
        print(f"   搜索: {task_info.get('search_query', 'unknown')}")
    elif intent in ["login", "open_and_login"]:
        print(f"   用户名: {task_info.get('username', 'unknown')}")
        print(f"   密码: {'*' * len(task_info.get('password', ''))}")
    elif intent == "open_website":
        print(f"   操作: 仅打开网站")
    
    print("-" * 60)
    
    # 验证必要字段
    required_fields = ['intent', 'website_url']
    missing_fields = []
    
    for field in required_fields:
        if field not in task_info or not task_info[field]:
            missing_fields.append(field)
    
    # 根据任务类型验证特定字段
    if intent == "open_and_search":
        if not task_info.get('search_query'):
            missing_fields.append('search_query')
    elif intent in ["login", "open_and_login"]:
        if not task_info.get('username'):
            missing_fields.append('username')
        if not task_info.get('password'):
            missing_fields.append('password')
    
    if missing_fields:
        print(f"⚠️  警告: 缺少字段 {missing_fields}")
        return False
    
    return True

async def main():
    """主函数"""
    print_welcome()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n请输入指令: ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['exit', 'quit', '退出', '结束']:
                print("👋 程序已退出，再见！")
                break
            
            # 检查空输入
            if not user_input:
                print("⚠️  请输入有效的指令")
                continue
            
            print(f"\n🔍 正在解析指令: {user_input}")
            print("=" * 50)
            
            # 解析用户输入
            task_info = parse_user_input(user_input)
            
            print("=" * 50)
            
            
            # 显示解析结果并验证
            is_valid = print_task_info(task_info)
            
            if not is_valid:
                print("❌ 任务信息不完整，无法执行")
                continue
            
            # 执行任务
            print("\n🚀 开始执行任务...")
            
            intent = task_info.get("intent")
            if intent in ["open_website", "open_and_search", "login", "open_and_login"]:
                controller = BrowserController()
                await controller.perform_task(task_info)
                print("✅ 任务执行完成！")
            else:
                print("⚠️  暂不支持此类型的任务")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！")
            break
        except Exception as e:
            print(f"❌ 执行任务时发生错误: {e}")
            print("请检查网络连接和API配置")

def run_single_command(command: str):
    """
    执行单个命令（用于测试）
    """
    async def single_task():
        try:
            print(f"执行命令: {command}")
            task_info = parse_user_input(command)
            is_valid = print_task_info(task_info)
            
            if not is_valid:
                print("❌ 任务信息不完整，无法执行")
                return
            
            intent = task_info.get("intent")
            if intent in ["open_website", "open_and_search", "login", "open_and_login"]:
                controller = BrowserController()
                await controller.perform_task(task_info)
                print("✅ 任务执行完成！")
            else:
                print("⚠️  暂不支持此类型的任务")
                
        except Exception as e:
            print(f"❌ 执行任务时发生错误: {e}")
    
    asyncio.run(single_task())

if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 如果有参数，执行单个命令
        command = " ".join(sys.argv[1:])
        run_single_command(command)
    else:
        # 否则进入交互模式
        asyncio.run(main())