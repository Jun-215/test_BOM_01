#!/usr/bin/env python3
"""
浏览器启动诊断工具
"""
import asyncio
import os
import time
from pyppeteer import launch
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

CHROME_PATH = os.getenv("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")

async def test_config_1():
    """测试配置1: 最小参数"""
    print("\n🧪 [测试1] 最小参数启动...")
    try:
        browser = await launch(
            headless=False,
            executablePath=CHROME_PATH,
            args=["--no-sandbox"],
            timeout=30000
        )
        print("✅ [测试1] 浏览器启动成功")
        
        page = await browser.newPage()
        await page.goto("https://www.baidu.com", {'timeout': 15000})
        print("✅ [测试1] 页面导航成功")
        
        await asyncio.sleep(3)
        await browser.close()
        print("✅ [测试1] 浏览器关闭成功")
        return True
        
    except Exception as e:
        print(f"❌ [测试1] 失败: {e}")
        return False

async def test_config_2():
    """测试配置2: 标准参数"""
    print("\n🧪 [测试2] 标准参数启动...")
    try:
        browser = await launch(
            headless=False,
            executablePath=CHROME_PATH,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ],
            timeout=30000
        )
        print("✅ [测试2] 浏览器启动成功")
        
        page = await browser.newPage()
        await page.goto("https://www.baidu.com", {'timeout': 15000})
        print("✅ [测试2] 页面导航成功")
        
        await asyncio.sleep(3)
        await browser.close()
        print("✅ [测试2] 浏览器关闭成功")
        return True
        
    except Exception as e:
        print(f"❌ [测试2] 失败: {e}")
        return False

async def test_config_3():
    """测试配置3: 完整参数"""
    print("\n🧪 [测试3] 完整参数启动...")
    try:
        browser = await launch(
            headless=False,
            executablePath=CHROME_PATH,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--window-size=1920,1080",
                "--remote-debugging-port=9222"
            ],
            timeout=30000
        )
        print("✅ [测试3] 浏览器启动成功")
        
        page = await browser.newPage()
        await page.goto("https://www.baidu.com", {'timeout': 15000})
        print("✅ [测试3] 页面导航成功")
        
        await asyncio.sleep(3)
        await browser.close()
        print("✅ [测试3] 浏览器关闭成功")
        return True
        
    except Exception as e:
        print(f"❌ [测试3] 失败: {e}")
        return False

async def test_chrome_path():
    """测试Chrome路径"""
    print("\n🔍 [检查] Chrome路径验证...")
    
    if os.path.exists(CHROME_PATH):
        print(f"✅ [检查] Chrome路径存在: {CHROME_PATH}")
        
        # 检查文件是否可执行
        if os.access(CHROME_PATH, os.X_OK):
            print("✅ [检查] Chrome文件可执行")
        else:
            print("⚠️  [检查] Chrome文件可能没有执行权限")
            
        return True
    else:
        print(f"❌ [检查] Chrome路径不存在: {CHROME_PATH}")
        
        # 尝试查找其他可能的路径
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', 'User'))
        ]
        
        print("🔍 [检查] 搜索其他可能的Chrome路径...")
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ [发现] 找到Chrome: {path}")
                return path
        
        print("❌ [检查] 未找到Chrome安装")
        return False

async def test_pyppeteer_version():
    """检查pyppeteer版本"""
    print("\n🔍 [检查] Pyppeteer版本信息...")
    try:
        import pyppeteer
        print(f"✅ [检查] Pyppeteer版本: {pyppeteer.__version__}")
        
        # 检查Chromium下载状态
        from pyppeteer.chromium_downloader import check_chromium
        if check_chromium():
            print("✅ [检查] Pyppeteer内置Chromium可用")
        else:
            print("⚠️  [检查] Pyppeteer内置Chromium不可用，将使用系统Chrome")
            
    except Exception as e:
        print(f"❌ [检查] Pyppeteer检查失败: {e}")

async def main():
    """主诊断程序"""
    print("🚀 浏览器启动诊断工具")
    print("=" * 50)
    
    # 1. 检查Chrome路径
    chrome_result = await test_chrome_path()
    if not chrome_result:
        print("\n❌ 诊断失败: Chrome浏览器未正确安装或路径配置错误")
        return
    
    # 2. 检查pyppeteer版本
    await test_pyppeteer_version()
    
    # 3. 测试不同配置
    print("\n🧪 开始测试不同的启动配置...")
    
    test_results = []
    test_results.append(("最小参数", await test_config_1()))
    test_results.append(("标准参数", await test_config_2()))
    test_results.append(("完整参数", await test_config_3()))
    
    # 4. 输出诊断报告
    print("\n" + "=" * 50)
    print("📊 诊断报告:")
    
    for config_name, result in test_results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"   {config_name}: {status}")
    
    # 5. 给出建议
    successful_configs = [name for name, result in test_results if result]
    
    if successful_configs:
        print(f"\n💡 建议: 使用 '{successful_configs[0]}' 配置")
        print("🔧 修改browser_controller.py中的launch参数")
    else:
        print("\n❌ 所有配置都失败了，可能的原因:")
        print("   1. Chrome版本不兼容")
        print("   2. 系统权限问题")
        print("   3. 防火墙阻止")
        print("   4. pyppeteer版本问题")
        print("\n💡 建议尝试:")
        print("   1. 以管理员权限运行")
        print("   2. 更新Chrome浏览器")
        print("   3. pip install --upgrade pyppeteer")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())