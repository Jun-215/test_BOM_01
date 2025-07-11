#!/usr/bin/env python3
"""
测试不同登录模式的自动切换功能
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser_controller import BrowserController

async def test_login_mode_detection():
    """测试登录模式检测和切换功能"""
    print("🧪 测试登录模式自动切换功能")
    print("=" * 60)
    
    controller = BrowserController()
    
    # 测试网站列表 - 这些网站通常有多种登录模式
    test_sites = [
        {
            "name": "知乎登录页",
            "url": "https://www.zhihu.com/signin",
            "test_username": "test_user",
            "test_password": "test_pass"
        },
        {
            "name": "微博登录页", 
            "url": "https://passport.weibo.cn/signin/login",
            "test_username": "test_user",
            "test_password": "test_pass"
        },
        {
            "name": "测试登录页面",
            "url": "https://the-internet.herokuapp.com/login",
            "test_username": "tomsmith",
            "test_password": "SuperSecretPassword!"
        }
    ]
    
    try:
        await controller.ensure_browser_ready()
        
        for i, site in enumerate(test_sites, 1):
            print(f"\n🌐 [测试{i}] 测试网站: {site['name']}")
            print(f"📍 [URL] {site['url']}")
            
            try:
                # 导航到登录页面
                await controller.goto_website(site['url'])
                await asyncio.sleep(3)  # 等待页面完全加载
                
                # 检测登录模式
                print("🔍 [步骤1] 检测当前登录模式...")
                await controller.detect_login_mode()
                
                # 分析页面元素
                print("📊 [步骤2] 分析页面登录元素...")
                await controller.debug_page_elements()
                
                # 尝试查找用户名输入框
                username_selectors = [
                    "input[name='username']",
                    "input[name='phone']", 
                    "input[type='text']",
                    "input[type='email']",
                    "input[type='tel']"
                ]
                
                print("👤 [步骤3] 测试用户名输入框查找...")
                try:
                    username_selector = await controller.find_element_with_debug(
                        username_selectors, "用户名输入框", 5000
                    )
                    print(f"✅ [成功] 找到用户名输入框: {username_selector}")
                except Exception as e:
                    print(f"❌ [失败] 未找到用户名输入框: {e}")
                
                # 尝试查找密码输入框
                password_selectors = [
                    "input[type='password']",
                    "input[name='password']"
                ]
                
                print("🔑 [步骤4] 测试密码输入框查找...")
                try:
                    password_selector = await controller.find_element_with_debug(
                        password_selectors, "密码输入框", 5000
                    )
                    print(f"✅ [成功] 找到密码输入框: {password_selector}")
                    
                    # 如果两个输入框都找到了，尝试登录
                    print(f"🔐 [步骤5] 尝试登录测试...")
                    await controller.login_to_website(site['test_username'], site['test_password'])
                    
                except Exception as e:
                    print(f"❌ [失败] 未找到密码输入框: {e}")
                    print("💡 这可能表示需要手动切换登录模式")
                
                print(f"✅ [完成] {site['name']} 测试完成\n")
                
            except Exception as e:
                print(f"❌ [错误] {site['name']} 测试失败: {e}")
                continue
        
        print("\n🎉 所有测试完成！")
        print("💡 浏览器将保持打开10秒供检查...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await controller.close_browser()

async def test_specific_login_scenario():
    """测试特定登录场景"""
    print("\n🎯 特定场景测试: 模拟用户提供手机号和密码，但页面是验证码模式")
    print("=" * 60)
    
    controller = BrowserController()
    
    try:
        await controller.ensure_browser_ready()
        
        # 测试知乎登录（通常默认是验证码模式）
        await controller.goto_website("https://www.zhihu.com/signin")
        await asyncio.sleep(3)
        
        print("📱 [场景] 用户输入了手机号和密码，但页面当前是短信验证码模式")
        print("🔄 [期望] 系统应该自动切换到密码登录模式")
        
        # 模拟用户登录请求
        await controller.login_to_website("13800138000", "mypassword123")
        
        print("✅ [测试完成] 检查是否成功切换并尝试登录")
        
    except Exception as e:
        print(f"❌ 特定场景测试失败: {e}")
    
    finally:
        await controller.close_browser()

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 完整测试 (测试多个网站)")
    print("2. 特定场景测试 (验证码->密码切换)")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_login_mode_detection())
    elif choice == "2":
        asyncio.run(test_specific_login_scenario())
    else:
        print("❌ 无效选择")